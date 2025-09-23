// static/js/chatbot.js
import { apiRequest } from "./api.js";

const chatbotToggle = document.getElementById("chatbot-toggle");
const chatbotWindow = document.getElementById("chatbot-window");
const chatbotClose = document.getElementById("chatbot-close");
const chatInput = document.getElementById("chat-input");
const sendMessageBtn = document.getElementById("send-message");
const chatMessages = document.getElementById("chat-messages");
const typingIndicator = document.getElementById("typing-indicator");

// A simple, local-only conversation history for demonstration
const conversationHistory = [
    { role: "model", text: "Hello! I am SmartBot, your AI banking assistant. How can I help you today?" }
];

// --- UI Functions ---
/**
 * Adds a new message bubble to the chat window.
 * @param {string} text The message content.
 * @param {string} sender 'user' or 'bot'.
 */
function addChatMessage(text, sender) {
    const messageContainer = document.createElement("div");
    messageContainer.classList.add("chat-message", `${sender}-message`);
    
    const messageBubble = document.createElement("div");
    messageBubble.textContent = text;
    messageContainer.appendChild(messageBubble);

    chatMessages.appendChild(messageContainer);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to the bottom
}

/**
 * Shows the typing indicator.
 */
function showTypingIndicator() {
    typingIndicator.classList.remove("hidden");
    chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to show indicator
}

/**
 * Hides the typing indicator.
 */
function hideTypingIndicator() {
    typingIndicator.classList.add("hidden");
}

/**
 * Handles the sending of a new message.
 */
async function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        // Add user message to the UI and history
        addChatMessage(message, "user");
        conversationHistory.push({ role: "user", text: message });

        // Clear input and disable controls
        chatInput.value = "";
        chatInput.disabled = true;
        sendMessageBtn.disabled = true;
        showTypingIndicator();

        try {
            // Call the chatbot API endpoint
            const res = await apiRequest("/chatbot", "POST", { message });
            
            if (res.ok) {
                // Add the bot's reply to the UI and history
                addChatMessage(res.data.reply, "bot");
                conversationHistory.push({ role: "bot", text: res.data.reply });
            } else {
                addChatMessage("Sorry, I'm having trouble connecting right now.", "bot");
            }
        } catch (error) {
            console.error("Chatbot API Error:", error);
            addChatMessage("An error occurred. Please try again later.", "bot");
        } finally {
            // Re-enable controls and hide typing indicator
            hideTypingIndicator();
            chatInput.disabled = false;
            sendMessageBtn.disabled = false;
            chatInput.focus();
        }
    }
}

/**
 * Initializes all chatbot event listeners.
 */
export function initChatbot() {
    // Initial message on load
    addChatMessage(conversationHistory[0].text, conversationHistory[0].role);

    // Toggle chatbot window
    chatbotToggle.addEventListener("click", () => {
        chatbotWindow.classList.toggle("hidden");
    });
    
    // Close chatbot window
    chatbotClose.addEventListener("click", () => {
        chatbotWindow.classList.add("hidden");
    });

    // Send message via button click
    sendMessageBtn.addEventListener("click", sendMessage);

    // Send message via Enter key press
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault(); // Prevent new line
            sendMessage();
        }
    });
}
