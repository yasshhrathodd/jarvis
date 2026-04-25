"""
Gemini API wrapper with tool-calling loop.

Flow:
  1. User message -> Gemini with tool schemas attached
  2. If Gemini wants to call tools, we call them, feed results back, repeat
  3. When Gemini returns plain text, we return that to the user

We cap iterations so Gemini can't get stuck in a tool-calling loop.
"""
import asyncio
import json
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

from .mcp_manager import get_tool_schemas, call_tool

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing. Set it in your .env file.")

genai.configure(api_key=API_KEY)

SYSTEM_INSTRUCTION = (
    "You are JARVIS, a personal AI assistant for a college student named Yash. "
    "You have tools to read his Gmail, read his Google Calendar, and search the web. "
    "Use tools freely whenever they would help answer the question. "
    "If a question needs data from multiple tools (e.g. comparing email content "
    "with calendar events), call them all before replying. "
    "Be concise, friendly, and natural — like a smart friend, not a textbook."
)

MAX_TOOL_ITERATIONS = 5


def _build_gemini_tools():
    """Convert internal schemas into Gemini's function-declaration format."""
    declarations = []
    for t in get_tool_schemas():
        params = t["parameters"]
        # Gemini wants a clean object schema
        clean = {
            "type": "object",
            "properties": params.get("properties", {}),
        }
        if params.get("required"):
            clean["required"] = params["required"]
        declarations.append({
            "name": t["name"],
            "description": t["description"],
            "parameters": clean,
        })
    return [{"function_declarations": declarations}]


class GeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=_build_gemini_tools(),
            system_instruction=SYSTEM_INSTRUCTION,
        )
        # Keep a single chat per client instance so conversation context persists
        self.chat = self.model.start_chat()

    async def send(self, user_message: str) -> str:
        """Send a user message, handle any tool calls, return final text reply."""
        response = await asyncio.to_thread(self.chat.send_message, user_message)

        for _ in range(MAX_TOOL_ITERATIONS):
            fn_calls = _extract_function_calls(response)
            if not fn_calls:
                break

            # Run all requested tools (sequentially; could be parallel)
            tool_responses = []
            for fc in fn_calls:
                args = dict(fc.args) if fc.args else {}
                result = call_tool(fc.name, args)
                tool_responses.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fc.name,
                            response={"result": json.dumps(result, default=str)},
                        )
                    )
                )

            response = await asyncio.to_thread(self.chat.send_message, tool_responses)

        return _extract_text(response) or "(JARVIS had nothing to say.)"

    def reset(self):
        """Start a fresh chat session (clears memory)."""
        self.chat = self.model.start_chat()


def _extract_function_calls(response) -> list:
    calls = []
    try:
        parts = response.candidates[0].content.parts
    except (AttributeError, IndexError):
        return calls
    for p in parts:
        fc = getattr(p, "function_call", None)
        if fc and fc.name:
            calls.append(fc)
    return calls


def _extract_text(response) -> str:
    chunks = []
    try:
        parts = response.candidates[0].content.parts
    except (AttributeError, IndexError):
        return ""
    for p in parts:
        text = getattr(p, "text", None)
        if text:
            chunks.append(text)
    return "".join(chunks).strip()
