/**
 * SPMS Frontend Runtime Configuration
 * Points to the live Render backend deployment.
 */
window.SPMS_CONFIG = {
    // Live Render Cloud Backend
    API_BASE_URL: localStorage.getItem('spms_backend_url') || 'https://spms-backend-jt6l.onrender.com',

    // Helper to get fully-qualified URL
    getUrl(path) {
        const cleanPath = path.startsWith('/') ? path : `/${path}`;
        const base = this.API_BASE_URL.replace(/\/+$/, '');
        return `${base}${cleanPath}`;
    },

    // Save custom backend URL if switched
    setBackendUrl(url) {
        if (!url) return;
        const normalized = url.trim().replace(/\/+$/, '');
        localStorage.setItem('spms_backend_url', normalized);
        this.API_BASE_URL = normalized;
    }
};
