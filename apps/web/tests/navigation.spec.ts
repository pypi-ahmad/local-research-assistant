import { expect, test } from "@playwright/test";

const paths = [
  "/",
  "/workspace",
  "/chat",
  "/documents",
  "/knowledge-base",
  "/search",
  "/ocr",
  "/notebooks",
  "/knowledge-graph",
  "/study-tools",
  "/flashcards",
  "/quizzes",
  "/settings",
  "/model-manager",
  "/monitoring"
];

test("all primary pages render", async ({ page }) => {
  for (const path of paths) {
    await page.goto(path);
    await expect(page.locator("h1")).toContainText("Local Research Assistant");
  }
});
