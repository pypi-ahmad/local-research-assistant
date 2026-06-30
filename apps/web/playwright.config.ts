import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  use: {
    baseURL: "http://127.0.0.1:13000",
    headless: true
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 13000",
    port: 13000,
    reuseExistingServer: true,
    timeout: 120_000
  }
});
