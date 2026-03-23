import { defineStore } from "pinia";
import api from "../api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || "",
    user: null,
  }),
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem("token", token);
    },
    clearToken() {
      this.token = "";
      this.user = null;
      localStorage.removeItem("token");
    },
    async fetchMe() {
      if (!this.token) {
        this.user = null;
        return null;
      }
      const resp = await api.get("/api/v1/users/me");
      this.user = resp.data;
      return this.user;
    },
  },
});
