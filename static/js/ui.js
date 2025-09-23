// static/js/ui.js

/**
 * Makes a specific modal visible on the screen.
 * @param {string} modalId The ID of the modal element to show.
 */
export function showModal(modalId) {
    document.getElementById(modalId)?.classList.remove("hidden");
}

/**
 * Hides all visible modals.
 */
export function closeModals() {
    document.querySelectorAll(".fixed.inset-0.z-50").forEach((modal) => {
        modal.classList.add("hidden");
    });
}

/**
 * Displays a temporary notification message on the screen.
 * @param {string} message The message to display.
 * @param {'info' | 'success' | 'error'} type The type of notification, which affects its color.
 * @param {number} duration The time in milliseconds before the notification disappears.
 */
export function showNotification(message, type = "info", duration = 4000) {
    const container = document.getElementById("notification-container");
    if (!container) return;

    const notification = document.createElement("div");
    notification.className = `notification ${type} animate-slide-right`;

    const iconClass = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-triangle' : 'fa-info-circle';
    
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${iconClass} mr-3"></i>
            <span>${message}</span>
            <button class="ml-auto text-white/70 hover:text-white">&times;</button>
        </div>
    `;

    const closeButton = notification.querySelector('button');
    closeButton.onclick = () => notification.remove();

    container.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, duration);
}


/**
 * Manages which main view is visible on the single-page application.
 * Hides all other views and shows the one with the specified ID.
 * @param {string} viewId The ID of the view element to display (e.g., 'homepage-view').
 */
export function showView(viewId) {
    document.querySelectorAll(".view").forEach((view) => {
        view.classList.add("hidden");
    });
    const viewToShow = document.getElementById(viewId);
    if(viewToShow) {
        viewToShow.classList.remove("hidden");
    } else {
        console.error(`View with id "${viewId}" not found.`);
        // Fallback to homepage if view is not found to prevent a blank screen.
        document.getElementById('homepage-view')?.classList.remove('hidden');
    }
}


/**
 * Loads content from an HTML <template> tag into a specified container.
 * This is used for populating dashboard sections without a full page reload.
 * @param {string} viewId The ID of the content view to load (e.g., 'user-dashboard-content').
 * @param {string} mainContentId The ID of the container element where the content will be injected.
 */
export function loadViewContent(viewId, mainContentId) {
    const template = document.getElementById(`${viewId.replace('-content', '')}-template`);
    const container = document.getElementById(mainContentId);

    if (template && container) {
        container.innerHTML = template.innerHTML;

        // Dispatch a custom event to signal that new content has been loaded.
        // This allows other parts of the application to react, e.g., to attach new event listeners.
        const event = new CustomEvent('contentLoaded', { detail: { viewId, container } });
        document.dispatchEvent(event);
    } else {
        console.error(`Template or container not found for view: ${viewId}`);
        container.innerHTML = `<p class="text-red-500">Error: Could not load content for this view.</p>`;
    }
}

