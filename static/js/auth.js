// static/js/auth.js

import { apiRequest } from "./api.js";
import { showModal, closeModals, showNotification, showView } from "./ui.js";
import { initUserDashboard, initAdminDashboard } from "./dashboard.js";

let pendingUserId = null; // Stores user ID during 2FA process

export async function handleUserLogin(e) {
    e.preventDefault();
    const username = e.target.elements["user-username"].value;
    const password = e.target.elements["user-password"].value;

    const res = await apiRequest("/login", "POST", { username, password });
    if (res.ok) {
        pendingUserId = res.data.user_id;
        closeModals();
        showModal("tfa-modal");
    } else {
        showNotification(res.data.message, "error");
    }
}

export async function handleAdminLogin(e) {
    e.preventDefault();
    const username = e.target.elements["admin-username"].value;
    const password = e.target.elements["admin-password"].value;

    const res = await apiRequest("/admin/login", "POST", { username, password });
    if (res.ok) {
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("username", res.data.username);
        localStorage.setItem("isAdmin", "true");
        closeModals();
        showNotification(`Welcome, ${res.data.username}!`, "success");
        initAdminDashboard();
    } else {
        showNotification(res.data.message, "error");
    }
}

export async function handleRegistration(e) {
    e.preventDefault();
    const username = e.target.elements["register-username"].value;
    const email = e.target.elements["register-email"].value;
    const password = e.target.elements["register-password"].value;

    const res = await apiRequest("/register", "POST", { username, email, password });
    if (res.ok) {
        showNotification("Registration successful! Please log in.", "success");
        closeModals();
        showModal("user-login-modal");
    } else {
        showNotification(res.data.message, "error");
    }
}

export async function verify2FA() {
    const code = document.getElementById("tfa-code").value;
    if (!code || !pendingUserId) {
        showNotification("Verification code is required.", "error");
        return;
    }

    const res = await apiRequest("/login/verify", "POST", { user_id: pendingUserId, code });

    if (res.ok) {
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("username", res.data.username);
        localStorage.setItem("isAdmin", "false");
        pendingUserId = null; // Clear after use
        closeModals();
        showNotification(`Welcome back, ${res.data.username}!`, "success");
        initUserDashboard();
    } else {
        showNotification(res.data.message, "error");
    }
}

export function logout() {
    localStorage.clear();
    // Use window.location to ensure a full page reload and state reset
    window.location.href = "/";
}
