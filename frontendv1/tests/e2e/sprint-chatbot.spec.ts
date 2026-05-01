import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Chatbot app", () => {
  test("chatbot page loads with session rail", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await expect(page).toHaveURL(/\/chatbot/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Simple chat-first UI." })).toBeVisible();
    await expect(page.getByTestId("session-rail")).toBeVisible();
  });

  test("chatbot page shows sessions in rail", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await expect(page.getByTestId("session-item").first()).toBeVisible();
    await expect(page.getByText("Story scene discussion")).toBeVisible();
    await expect(page.getByText("Care update draft")).toBeVisible();
  });

  test("chatbot page has new conversation button", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await expect(page.getByTestId("new-session-button")).toBeVisible();
  });

  test("selecting a session loads messages", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await page.getByText("Story scene discussion").click();

    await expect(page.getByTestId("chatbot-messages")).toBeVisible();
    await expect(page.getByText("Can you help me outline a scene?")).toBeVisible();
    await expect(page.getByText("Of course! Start with the setting")).toBeVisible();
  });

  test("chatbot shows per-turn token and cost data", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await page.getByText("Story scene discussion").click();

    await expect(page.getByText(/tokens/)).toBeVisible();
    await expect(page.getByText("gpt-4o")).toBeVisible();
  });

  test("sending a message shows pending state and then reply", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await page.getByText("Story scene discussion").click();
    await page.getByTestId("chatbot-input").fill("What is the best opening hook?");
    await page.getByRole("button", { name: "Send message" }).click();

    await expect(page.getByTestId("assistant-pending")).toBeVisible();

    await expect(page.getByText("Understood. Here is a helpful response.")).toBeVisible({ timeout: 10000 });
  });

  test("starter prompts send message to active session", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await page.getByText("Story scene discussion").click();
    await page.getByTestId("starter-prompt").first().click();

    await expect(page.getByText("Understood. Here is a helpful response.")).toBeVisible({ timeout: 10000 });
  });

  test("creating new session clears messages area", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await page.getByTestId("new-session-button").click();

    await expect(page.getByTestId("empty-session")).toBeVisible({ timeout: 5000 });
  });

  test("send error shows retry control", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/chatbot/sessions/*/messages", async (route) => {
      if (route.request().method() === "POST") {
        await route.fulfill({ status: 500, contentType: "application/json",
          body: JSON.stringify({ detail: "Failed to process message" }) });
      } else {
        await route.fallback();
      }
    });
    await page.goto("/chatbot");

    await page.getByText("Story scene discussion").click();
    await page.getByTestId("chatbot-input").fill("Test message");
    await page.getByRole("button", { name: "Send message" }).click();

    await expect(page.getByTestId("send-error")).toBeVisible({ timeout: 8000 });
    await expect(page.getByText("Retry")).toBeVisible();
  });

  test("chatbot page auth guard redirects when not authenticated", async ({ page }) => {
    await mockAppApis(page, { session: "anonymous" });
    await page.goto("/chatbot");

    await expect(page).not.toHaveURL(/\/chatbot$/, { timeout: 15000 });
  });

  test("session restore via direct URL loads session", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot/sessions/10");

    await expect(page.getByTestId("chatbot-messages")).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("Can you help me outline a scene?")).toBeVisible();
  });

  test("history page lists sessions with delete option", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot/history");

    await expect(page.getByRole("heading", { name: "Conversation History" })).toBeVisible();
    await expect(page.getByText("Story scene discussion")).toBeVisible();
    await expect(page.getByTestId("history-delete-session").first()).toBeVisible();
  });

  test("settings page shows usage information", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot/settings");

    await expect(page.getByRole("heading", { name: "Chatbot Settings" })).toBeVisible();
    await expect(page.getByText("GPT-4o")).toBeVisible();
  });

  test("create session and send from empty state", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot");

    await page.getByTestId("chatbot-input").fill("Hello AI");
    await page.getByRole("button", { name: "Send message" }).click();

    await expect(page.getByTestId("assistant-pending")).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("Understood. Here is a helpful response.")).toBeVisible({ timeout: 10000 });
  });

  test("sessions page redirects to chatbot root", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/chatbot/sessions");

    await expect(page).toHaveURL(/\/chatbot/, { timeout: 5000 });
  });
});
