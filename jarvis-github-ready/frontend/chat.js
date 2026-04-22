// JARVIS chat frontend logic

const API_URL = window.location.origin;

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send-btn");
const resetBtn = document.getElementById("reset-btn");

let isFirstMessage = true;

// Auto-resize textarea
inputEl.addEventListener("input", () => {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 200) + "px";
});

// Submit on Enter (Shift+Enter for newline)
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    formEl.dispatchEvent(new Event("submit"));
  }
});

// Suggestion chips
document.querySelectorAll(".suggestion").forEach((btn) => {
  btn.addEventListener("click", () => {
    inputEl.value = btn.textContent;
    inputEl.focus();
    formEl.dispatchEvent(new Event("submit"));
  });
});

// Reset chat
resetBtn.addEventListener("click", async () => {
  if (!confirm("Start a new chat? Current conversation will be lost.")) return;
  try {
    await fetch(`${API_URL}/reset`, { method: "POST" });
  } catch (e) {
    console.error(e);
  }
  messagesEl.innerHTML = `
    <div class="welcome">
      <h2>Hey Y-Dawg.</h2>
      <p>Ask me about your emails, your schedule, or anything on the web.</p>
    </div>
  `;
  isFirstMessage = true;
});

// Submit handler
formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;

  // Clear welcome screen on first message
  if (isFirstMessage) {
    messagesEl.innerHTML = "";
    isFirstMessage = false;
  }

  appendMessage("user", text);
  inputEl.value = "";
  inputEl.style.height = "auto";
  setSending(true);

  const typingNode = appendTyping();

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    typingNode.remove();

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      appendMessage("bot", `Error: ${err.detail || res.statusText}`, true);
    } else {
      const data = await res.json();
      appendMessage("bot", data.reply || "(empty reply)");
    }
  } catch (err) {
    typingNode.remove();
    appendMessage("bot", `Network error: ${err.message}. Is the backend running?`, true);
  } finally {
    setSending(false);
    inputEl.focus();
  }
});

function appendMessage(role, text, isError = false) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}${isError ? " error" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "Y" : "J";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return wrap;
}

function appendTyping() {
  const wrap = document.createElement("div");
  wrap.className = "message bot";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "J";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = `<div class="typing"><span></span><span></span><span></span></div>`;

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return wrap;
}

function setSending(busy) {
  sendBtn.disabled = busy;
  inputEl.disabled = busy;
}
