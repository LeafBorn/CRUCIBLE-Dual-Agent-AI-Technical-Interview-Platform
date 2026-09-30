// Shared API helper and Auth manager
const API = {
  getToken() {
    return localStorage.getItem("interview_token");
  },

  getUsername() {
    return localStorage.getItem("interview_username");
  },

  setAuth(token, username) {
    localStorage.setItem("interview_token", token);
    localStorage.setItem("interview_username", username);
  },

  clearAuth() {
    localStorage.removeItem("interview_token");
    localStorage.removeItem("interview_username");
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = "/login";
      return false;
    }
    return true;
  },

  async request(url, options = {}) {
    const headers = options.headers || {};
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && options.body && typeof options.body === "object") {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(options.body);
    }

    options.headers = headers;

    try {
      const res = await fetch(url, options);
      if (res.status === 401) {
        this.clearAuth();
        window.location.href = "/login";
        return null;
      }
      
      const contentType = res.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || data.message || "An error occurred");
        }
        return data;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
      }
      return res;
    } catch (err) {
      console.error("API Request Error:", err);
      throw err;
    }
  },

  get(url) {
    return this.request(url, { method: "GET" });
  },

  post(url, data) {
    return this.request(url, { method: "POST", body: data });
  },

  put(url, data) {
    return this.request(url, { method: "PUT", body: data });
  },

  upload(url, formData) {
    return this.request(url, {
      method: "POST",
      body: formData
    });
  },

  logout() {
    this.clearAuth();
    window.location.href = "/login";
  },

  renderUserBadge() {
    const userDisplay = document.getElementById("navUsername");
    if (userDisplay) {
      const username = this.getUsername();
      userDisplay.textContent = username || "User";
    }
  }
};
