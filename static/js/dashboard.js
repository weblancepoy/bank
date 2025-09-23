// static/js/dashboard.js
import { showView, loadViewContent } from "./ui.js";

export function initUserDashboard() {
    showView("user-dashboard");
    document.getElementById("chatbot-container").classList.remove("hidden");
    const username = localStorage.getItem("username") || "User";
    const sidebarUsername = document.getElementById("sidebar-username");
    if(sidebarUsername) sidebarUsername.textContent = username;
    
    setupNavigation("user-sidebar-nav", "user-main-content", false);
    loadViewContent("user-dashboard-content", "user-main-content");
}

export function initAdminDashboard() {
    showView("admin-dashboard");
    setupNavigation("admin-sidebar-nav", "admin-main-content", true);
    loadViewContent("admin-dashboard-content", "admin-main-content");
}

function setupNavigation(containerId, mainContentId, isAdminNav) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.addEventListener("click", (e) => {
        const link = e.target.closest("a");
        if (link && link.dataset.view) {
            e.preventDefault();
            container.querySelectorAll("a").forEach(i => i.classList.remove("active"));
            link.classList.add("active");
            loadViewContent(link.dataset.view, mainContentId);
        }
    });
}
