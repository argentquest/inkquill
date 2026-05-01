import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Prompt library", () => {
  test("prompts page loads my prompts list", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/prompts");

    await expect(page).toHaveURL(/\/storytelling\/prompts/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Prompt Library" })).toBeVisible();
    await expect(page.getByTestId("my-prompts-list")).toBeVisible();
    await expect(page.getByText("Fantasy world opener")).toBeVisible();
    await expect(page.getByText("Character backstory hook")).toBeVisible();
  });

  test("prompts page shows empty state when no prompts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/prompts/my-prompts*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }) });
    });
    await page.goto("/storytelling/prompts");

    await expect(page).toHaveURL(/\/storytelling\/prompts/, { timeout: 15000 });
    await expect(page.getByTestId("my-prompts-empty")).toBeVisible();
    await expect(page.getByText("No prompts yet")).toBeVisible();
  });

  test("prompts page has new prompt button", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/prompts");

    await expect(page.getByTestId("new-prompt-button")).toBeVisible();
    await page.getByTestId("new-prompt-button").click();
    await expect(page.getByTestId("new-prompt-form")).toBeVisible();
  });

  test("new prompt form submits and dismisses", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/prompts");

    await page.getByTestId("new-prompt-button").click();
    await page.locator("#prompt-title").fill("Tension builder");
    await page.locator("#prompt-content").fill("Write a paragraph that builds tension before a major reveal.");
    await page.getByRole("button", { name: "Save prompt" }).click();

    await expect(page.getByTestId("new-prompt-form")).not.toBeVisible({ timeout: 5000 });
  });

  test("prompt card has delete button", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/prompts");

    await expect(page.getByTestId("delete-prompt-button").first()).toBeVisible();
  });

  test("prompts page auth guard redirects when not authenticated", async ({ page }) => {
    await mockAppApis(page, { session: "anonymous" });
    await page.goto("/storytelling/prompts");

    await expect(page).not.toHaveURL(/\/storytelling\/prompts$/, { timeout: 15000 });
  });
});

test.describe("AI models", () => {
  test("AI models page loads model catalog", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/ai-models");

    await expect(page).toHaveURL(/\/storytelling\/ai-models/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "AI Models" })).toBeVisible();
    await expect(page.getByTestId("active-models-list")).toBeVisible();
    await expect(page.getByText("GPT-4o")).toBeVisible();
    await expect(page.getByText("Claude 3 Haiku")).toBeVisible();
  });

  test("AI models page shows summary stats", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/ai-models");

    await expect(page.getByTestId("models-summary")).toBeVisible();
    await expect(page.getByText("2")).toBeVisible();
  });

  test("AI models page shows empty state when no models", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/llm-models/**", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify({ success: true, data: { models: [], total_count: 0, active_count: 0, providers: [] } }) });
    });
    await page.goto("/storytelling/ai-models");

    await expect(page.getByTestId("models-empty-state")).toBeVisible();
    await expect(page.getByText("No AI models configured")).toBeVisible();
  });

  test("AI models page shows error state when API fails", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/llm-models/**", async (route) => {
      await route.fulfill({ status: 500, contentType: "application/json",
        body: JSON.stringify({ success: false }) });
    });
    await page.goto("/storytelling/ai-models");

    await expect(page.getByText("AI models could not be loaded.")).toBeVisible();
  });
});

test.describe("Blog authoring", () => {
  test("blog dashboard loads drafts and published posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog");

    await expect(page).toHaveURL(/\/storytelling\/blog$/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Blog" })).toBeVisible();
    await expect(page.getByTestId("blog-drafts-list")).toBeVisible();
    await expect(page.getByTestId("blog-published-list")).toBeVisible();
    await expect(page.getByText("My First Blog Post")).toBeVisible();
    await expect(page.getByText("Writing Tips for Fantasy")).toBeVisible();
  });

  test("blog dashboard shows empty state when no posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/blog/posts**", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }) });
    });
    await page.goto("/storytelling/blog");

    await expect(page.getByTestId("blog-empty-state")).toBeVisible();
    await expect(page.getByText("No blog posts yet")).toBeVisible();
  });

  test("blog dashboard has new post link", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog");

    await page.getByRole("link", { name: "New post" }).first().click();
    await expect(page).toHaveURL(/\/storytelling\/blog\/new/, { timeout: 15000 });
  });

  test("new blog post page renders form", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog/new");

    await expect(page.getByTestId("post-title-input")).toBeVisible();
    await expect(page.getByTestId("post-content-input")).toBeVisible();
    await expect(page.getByRole("button", { name: "Save draft" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Publish" })).toBeVisible();
  });

  test("new blog post page saves draft and redirects", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog/new");

    await page.getByTestId("post-title-input").fill("A tale of two cities");
    await page.getByTestId("post-content-input").fill("It was the best of times.");
    await page.getByRole("button", { name: "Save draft" }).click();

    await expect(page).toHaveURL(/\/storytelling\/blog$/, { timeout: 15000 });
  });

  test("blog post edit page loads existing post", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog/201");

    await expect(page).toHaveURL(/\/storytelling\/blog\/201/, { timeout: 15000 });
    await expect(page.getByTestId("edit-title-input")).toHaveValue("My First Blog Post");
    await expect(page.getByTestId("edit-content-input")).toBeVisible();
  });

  test("blog media manager renders upload button and empty state", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/blog/media/list*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }) });
    });
    await page.goto("/storytelling/blog/media");

    await expect(page).toHaveURL(/\/storytelling\/blog\/media/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Media Library" })).toBeVisible();
    await expect(page.getByTestId("upload-media-button")).toBeVisible();
    await expect(page.getByTestId("media-empty-state")).toBeVisible();
  });
});

test.describe("Referral intro panel", () => {
  test("referrals page shows intro panel with referral link", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/referrals");

    await expect(page).toHaveURL(/\/storytelling\/referrals/, { timeout: 15000 });
    await expect(page.getByTestId("referral-intro-panel")).toBeVisible();
    await expect(page.getByText("Invite friends, earn coins")).toBeVisible();
    await expect(page.getByTestId("referral-url")).toBeVisible();
    await expect(page.getByTestId("copy-referral-link")).toBeVisible();
  });
});
