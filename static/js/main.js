// static/js/main.js
import { handleUserLogin, handleAdminLogin, handleRegistration, verify2FA, logout } from "./auth.js";
import { initUserDashboard, initAdminDashboard } from "./dashboard.js";
import { showModal, closeModals, showView } from "./ui.js";
import { initChatbot } from "./chatbot.js";

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    const isAdmin = localStorage.getItem("isAdmin") === "true";

    if (token) {
        if (isAdmin) {
            initAdminDashboard();
        } else {
            initUserDashboard();
        }
    } else {
        showView('homepage-view');
    }

    // --- Event Listeners Setup ---
    
    // Auth Forms
    document.getElementById("user-login-form")?.addEventListener("submit", handleUserLogin);
    document.getElementById("admin-login-form")?.addEventListener("submit", handleAdminLogin);
    document.getElementById("register-form")?.addEventListener("submit", handleRegistration);

    // Modal Triggers
    document.querySelectorAll("[data-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            showModal(button.dataset.modal);
        });
    });

    // Modal Close Buttons
    document.querySelectorAll(".close-modal").forEach((button) => {
        button.addEventListener("click", closeModals);
    });

    // 2FA Verification
    document.getElementById("verify-2fa-btn")?.addEventListener("click", verify2FA);

    // Logout Buttons
    document.querySelectorAll(".logout-btn").forEach((button) => {
        button.addEventListener("click", logout);
    });

    // Initialize chatbot functionality
    initChatbot();
});
