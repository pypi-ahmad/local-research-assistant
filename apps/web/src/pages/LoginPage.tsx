import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../services/api";
import { useAuthStore } from "../stores/auth";

export function LoginPage() {
  const navigate = useNavigate();
  const { setToken } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const login = async () => {
    try {
      const response = await api.post("/auth/login", { email, password });
      setToken(response.data.access_token);
      localStorage.setItem("lra_refresh_token", response.data.refresh_token);
      navigate("/");
    } catch (err) {
      setError("Login failed. Check credentials.");
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-base-950 px-4">
      <section className="w-full max-w-md rounded-2xl border border-base-800 bg-base-900/80 p-6">
        <h1 className="font-display text-3xl text-white">Local Research Assistant</h1>
        <p className="mt-1 text-sm text-slate-400">Login with your local account</p>
        <div className="mt-5 space-y-3">
          <input
            className="w-full rounded-xl border border-base-700 bg-base-950 px-4 py-3"
            placeholder="Email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <input
            className="w-full rounded-xl border border-base-700 bg-base-950 px-4 py-3"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <button className="w-full rounded-xl bg-accent-500 px-5 py-3 font-semibold text-base-950" onClick={() => void login()} type="button">
            Login
          </button>
          {error ? <p className="text-sm text-signal-red">{error}</p> : null}
        </div>
      </section>
    </main>
  );
}
