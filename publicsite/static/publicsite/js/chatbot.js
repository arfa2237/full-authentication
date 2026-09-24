const chatbotBtn = document.getElementById("chatbot-btn");
const chatbotBox = document.getElementById("chatbot-box");
const closeChat  = document.getElementById("close-chat");
const chatBody   = document.querySelector(".chat-body");
const chatInput  = document.getElementById("chat-input");

const HISTORY_KEY = "tig_chat_history";
const OPEN_KEY    = "tig_chat_open";

function loadHistory() {
    try { return JSON.parse(sessionStorage.getItem(HISTORY_KEY)) || []; }
    catch { return []; }
}

function saveHistory() {
    try { sessionStorage.setItem(HISTORY_KEY, JSON.stringify(chatHistory.slice(-20))); }
    catch (e) { console.error("Could not save chat", e); }
}

function setOpen(isOpen) {
    chatbotBox.style.display = isOpen ? "flex" : "none";
    try { sessionStorage.setItem(OPEN_KEY, isOpen ? "1" : "0"); } catch {}
}

let chatHistory  = loadHistory();
let introRemoved = false;

function removeIntro() {
    chatBody.querySelectorAll(":scope > p.bot-msg").forEach(el => el.remove());
    introRemoved = true;
}

// save chat on every page...
function restoreChat() {
    if (chatHistory.length === 0) return;
    removeIntro();
    chatHistory.forEach(m => {
        if (m.role === "user") appendMessage("user", m.content);
        else createBotBubble().innerHTML = renderMarkdown(m.content);
    });
    chatBody.scrollTop = chatBody.scrollHeight;
}

restoreChat();
if (sessionStorage.getItem(OPEN_KEY) === "1") setOpen(true);  

chatbotBtn.onclick = () => {
    setOpen(true);                        
    chatInput.focus();
};

closeChat.onclick = () => {
    setOpen(false);                       
};

// Enter btn fo msg send 
chatInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send function 
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    removeIntro();

    // Show user bubble
    appendMessage("user", message);
    chatHistory.push({ role: "user", content: message });
    chatInput.value = "";
    chatInput.disabled = true;

    // Show typing dots
    const typingEl = showTyping();

    const rollbackUserMsg = () => {
        if (chatHistory.length && chatHistory[chatHistory.length - 1].role === "user") {
            chatHistory.pop();
        }
    };
    try {
        const res = await fetch("/chatbot/", {
            method : "POST",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify({
                message: message,
                history: chatHistory.slice(0, -1),
            }),
        });

        if (!res.ok) {
            let errMsg = "Server error.";
            try { errMsg = (await res.json()).error || errMsg; } catch {}
            removeTyping(typingEl);
            rollbackUserMsg();
            appendMessage("bot", "⚠️ " + errMsg);
            chatInput.disabled = false;
            return;
        }

        // Stream tokens via SSE
        const reader  = res.body.getReader();
        const decoder = new TextDecoder();
        let   buffer  = "";
        let   botBubble = null;    
        let   fullReply = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop(); 

            for (const line of lines) {
                if (!line.startsWith("data: ")) continue;
                const raw = line.slice(6).trim();
                if (raw === "[DONE]") break;

                let parsed;
                try { parsed = JSON.parse(raw); } catch { continue; }

                if (parsed.error) {
                    removeTyping(typingEl);
                    appendMessage("bot", "⚠️ " + parsed.error);
                    chatInput.disabled = false;
                    return;
                }

                if (parsed.token) {
                    // Remove typing dots
                    if (botBubble === null) {
                        removeTyping(typingEl);
                        botBubble = createBotBubble();
                    }
                    fullReply += parsed.token;
                    // Render markdown live 
                    botBubble.innerHTML = renderMarkdown(fullReply);
                    chatBody.scrollTop = chatBody.scrollHeight;
                }
            }
        }

        // Save full reply to history
        if (fullReply) {
            chatHistory.push({ role: "assistant", content: fullReply });
            saveHistory();
        } else {
            removeTyping(typingEl);
            rollbackUserMsg();
        }

    } catch (err) {
        removeTyping(typingEl);
        rollbackUserMsg();
        appendMessage("bot", "⚠️ Network error. Is the server running?");
        console.error(err);
    }

    chatInput.disabled = false;
    chatInput.focus();
}

// empty bot bubble
function createBotBubble() {
    removeIntro();
    const wrapper = document.createElement("div");
    wrapper.classList.add("msg-wrapper", "msg-bot-wrap");

    const bubble = document.createElement("div");
    bubble.classList.add("bot-msg");

    wrapper.appendChild(bubble);
    chatBody.appendChild(wrapper);
    chatBody.scrollTop = chatBody.scrollHeight;
    return bubble;
}

// Append a complete bubble (user msg)
function appendMessage(role, text) {
    removeIntro();
    const wrapper = document.createElement("div");
    wrapper.classList.add(
        "msg-wrapper",
        role === "user" ? "msg-user-wrap" : "msg-bot-wrap"
    );
    const bubble = document.createElement("div");
    bubble.classList.add(role === "user" ? "user-msg" : "bot-msg");
    bubble.innerText = text;
    wrapper.appendChild(bubble);
    chatBody.appendChild(wrapper);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Convert 
function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/^(\d+)\.\s+(.+)$/gm,
            "<div class='chat-list-item'><span class='chat-num'>$1.</span><span class='chat-text'>$2</span></div>")
        .replace(/^-\s+(.+)$/gm,
            "<div class='chat-list-item'><span class='chat-num'>•</span><span class='chat-text'>$1</span></div>")
        .replace(/\n{2,}/g, "<br><br>")
        .replace(/\n/g, "<br>");
}

// Typing dots
function showTyping() {
    const el = document.createElement("div");
    el.classList.add("msg-wrapper", "msg-bot-wrap");
    el.id = "typing-indicator";
    el.innerHTML = `<div class="bot-msg typing-indicator">
        <span></span><span></span><span></span>
    </div>`;
    chatBody.appendChild(el);
    chatBody.scrollTop = chatBody.scrollHeight;
    return el;
}

function removeTyping(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
}

