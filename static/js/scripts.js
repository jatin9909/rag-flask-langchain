document.addEventListener("DOMContentLoaded", function() {
    const nextButton = document.getElementById("next-button");
    const chatSection = document.getElementById("chat-section");
    const uploadSection = document.getElementById("upload-section");
    const sendButton = document.getElementById("send-button");
    const userInput = document.getElementById("user-input");
    const chatbox = document.getElementById("chatbox");
    const clearSessionButton = document.getElementById("clear-session-button");

    nextButton.addEventListener("click", function() {
        const files = document.getElementById("file-input").files;
        if (files.length > 0) {
            // Handle file uploads here
            console.log("Files uploaded:", files);
            // Move to chat section
            uploadSection.style.display = "none";
            chatSection.style.display = "flex";
        } else {
            alert("Please upload at least one document.");
        }
    });

    sendButton.addEventListener("click", function() {
        sendMessage();
    });

    userInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    clearSessionButton.addEventListener("click", function() {
        fetch("/reset_history", {
            method: "GET"
        })
        .then(() => {
            chatbox.innerHTML = "";
            alert("Session cleared!");
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });

    function sendMessage() {
        const message = userInput.value;
        if (message.trim() === "") return;

        // Display user's message
        const userMessageDiv = document.createElement("div");
        userMessageDiv.classList.add("user-message");
        const messageText = document.createElement("div");
        messageText.classList.add("message-text");
        messageText.textContent = message;
        userMessageDiv.appendChild(messageText);
        chatbox.appendChild(userMessageDiv);

        // Clear input field
        userInput.value = "";

        // Scroll chatbox to bottom
        chatbox.scrollTop = chatbox.scrollHeight;

        // Send message to server and get response
        fetch("/send", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Display bot's response
            const botMessageDiv = document.createElement("div");
            botMessageDiv.classList.add("bot-message");
            const botMessageText = document.createElement("div");
            botMessageText.classList.add("message-text");
            botMessageText.textContent = data.response;
            botMessageDiv.appendChild(botMessageText);
            chatbox.appendChild(botMessageDiv);

            // Scroll chatbox to bottom
            chatbox.scrollTop = chatbox.scrollHeight;
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }
});
