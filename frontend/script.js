const API_URL = "http://localhost:8000";

let sessionId = localStorage.getItem("northstar_session_id");

const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const typing = document.getElementById("typing");

function addMessage(role, text) {
    const message = document.createElement("div");
    message.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "Y" : "N";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    message.appendChild(avatar);
    message.appendChild(bubble);

    chatBox.appendChild(message);

    chatBox.scrollTop = chatBox.scrollHeight;
}

function setLoading(isLoading) {
    sendBtn.disabled = isLoading;
    messageInput.disabled = isLoading;
    typing.style.display = isLoading ? "block" : "none";
}

async function sendMessage(text = null) {
    const message = text || messageInput.value.trim();

    if (!message) {
        return;
    }

    addMessage("user", message);

    messageInput.value = "";
    setLoading(true);

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        sessionId = data.session_id;

        localStorage.setItem(
            "northstar_session_id",
            sessionId
        );

        addMessage("assistant", data.reply);

    } catch (error) {
        console.error(error);

        addMessage(
            "assistant",
            "Sorry, I'm unable to respond right now. Please try again."
        );
    } finally {
        setLoading(false);
        messageInput.focus();
    }
}

async function resetConversation() {
    try {
        if (sessionId) {
            await fetch(`${API_URL}/reset`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });
        }
    } catch (error) {
        console.error("Reset error:", error);
    }

    sessionId = null;
    localStorage.removeItem("northstar_session_id");

    chatBox.innerHTML = "";

    addMessage(
        "assistant",
        "Hi! 👋 Welcome to Northstar Homes. I'm your virtual sales assistant for Northstar One, Sector 79, Gurugram. How can I help you today?"
    );

    messageInput.focus();
}

sendBtn.addEventListener("click", () => {
    sendMessage();
});

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

resetBtn.addEventListener("click", resetConversation);

document.querySelectorAll(".quick-actions button").forEach((button) => {
    button.addEventListener("click", () => {
        sendMessage(button.dataset.message);
    });
});

messageInput.focus();