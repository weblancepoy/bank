// static/js/api.js

/**
 * A centralized function for making API requests.
 * It automatically includes the auth token and handles basic error scenarios.
 * @param {string} endpoint The API endpoint to call (e.g., '/login').
 * @param {string} method The HTTP method (e.g., 'GET', 'POST').
 * @param {object|null} body The request body for POST/PUT requests.
 * @returns {Promise<{ok: boolean, data: any, isCsv?: boolean}>} An object with the request status and data.
 */
export async function apiRequest(endpoint, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = localStorage.getItem("token");
    if (token) {
        headers["x-access-token"] = token;
    }

    try {
        const response = await fetch(`/api${endpoint}`, {
            method,
            headers,
            body: body ? JSON.stringify(body) : null,
        });

        // Handle file downloads separately from JSON
        const contentType = response.headers.get("Content-Type");
        if (contentType && contentType.includes("text/csv")) {
            if (!response.ok) throw new Error('Failed to download file');
            return {
                ok: true,
                data: await response.text(),
                isCsv: true,
            };
        }

        const data = await response.json();

        // If unauthorized, redirect to home to log in again
        if (response.status === 401 && endpoint !== '/login') {
            logout();
        }

        return { ok: response.ok, data };
    } catch (error) {
        console.error("API Request Error:", { endpoint, error });
        // Return a consistent error structure
        return { ok: false, data: { message: "Network or server error." } };
    }
}
