import { create } from "zustand";

interface AuthState {
  token: string | null;
  setToken: (token: string | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem("lra_access_token"),
  setToken: (token) => {
    if (token) {
      localStorage.setItem("lra_access_token", token);
    } else {
      localStorage.removeItem("lra_access_token");
    }
    set({ token });
  }
}));
