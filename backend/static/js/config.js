/**
 * SPMS Frontend Runtime Configuration
 * Allows configuring the Render backend API endpoint dynamically.
 */
window.SPMS_CONFIG = {
    // Default fallback to current host or Render cloud backend
    API_BASE_URL: localStorage.getItem('spms_backend_url') || window.location.origin,

    // Helper to get fully-qualified URL
    getUrl(path) {
        const cleanPath = path.startsWith('/') ? path : `/${path}`;
        const base = this.API_BASE_URL.replace(/\/+$/, '');
        return `${base}${cleanPath}`;
    },

    // Save custom backend URL
    setBackendUrl(url) {
        if (!url) return;
        const normalized = url.trim().replace(/\/+$/, '');
        localStorage.setItem('spms_backend_url', normalized);
        this.API_BASE_URL = normalized;
    }
};
