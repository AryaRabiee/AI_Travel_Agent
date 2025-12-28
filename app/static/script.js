async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    const typing = addMessage("در حال فکر کردن...", "bot");

    try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await res.json();
        typing.remove();
        typeText(data.answer || data, "bot");

    } catch {
        typing.innerText = "❌ خطا در ارتباط با سرور";
    }
}

function addMessage(text, sender) {
    const box = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerText = text;
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
    return msg;
}

function typeText(text, sender) {
    const box = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    box.appendChild(msg);

    let i = 0;
    const interval = setInterval(() => {
        msg.innerText += text[i];
        i++;
        box.scrollTop = box.scrollHeight;
        if (i >= text.length) clearInterval(interval);
    }, 15);
}
