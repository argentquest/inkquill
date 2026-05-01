import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Storytelling boundary routes", () => {
  // ---------------------------------------------------------------------------
  // Stories route
  // ---------------------------------------------------------------------------

  test("stories route loads user story list", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/stories");

    await expect(page).toHaveURL(/\/storytelling\/stories/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Your Stories" })).toBeVisible();
    await expect(page.getByTestId("stories-list")).toBeVisible();
    await expect(page.getByText("The Silver Compass")).toBeVisible();
    await expect(page.getByText("Ember Coast")).toBeVisible();
    await expect(page.getByText("Fantasy Adventure")).toBeVisible();
  });

  test("stories route shows empty state when user has no stories", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/stories/", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }),
      });
    });
    await page.goto("/storytelling/stories");

    await expect(page).toHaveURL(/\/storytelling\/stories/, { timeout: 15000 });
    await expect(page.getByTestId("stories-empty-state")).toBeVisible();
    await expect(page.getByText("No stories yet")).toBeVisible();
    await expect(page.getByRole("button", { name: "Create a story" })).toBeVisible();
  });

  test("stories route shows error state when API fails", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/stories/", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false }),
      });
    });
    await page.goto("/storytelling/stories");

    await expect(page).toHaveURL(/\/storytelling\/stories/, { timeout: 15000 });
    await expect(page.getByText("Stories could not be loaded.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Reload stories" })).toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // Worlds route
  // ---------------------------------------------------------------------------

  test("worlds route loads user world list", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/worlds");

    await expect(page).toHaveURL(/\/storytelling\/worlds/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Your Worlds" })).toBeVisible();
    await expect(page.getByTestId("worlds-list")).toBeVisible();
    await expect(page.getByText("Aethoria")).toBeVisible();
    await expect(page.getByText("floating islands")).toBeVisible();
  });

  test("worlds route shows empty state when user has no worlds", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/worlds/", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }),
      });
    });
    await page.goto("/storytelling/worlds");

    await expect(page).toHaveURL(/\/storytelling\/worlds/, { timeout: 15000 });
    await expect(page.getByTestId("worlds-empty-state")).toBeVisible();
    await expect(page.getByText("No worlds yet")).toBeVisible();
    await expect(page.getByRole("button", { name: "Create a world" })).toBeVisible();
  });

  test("worlds route shows error state when API fails", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/worlds/", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false }),
      });
    });
    await page.goto("/storytelling/worlds");

    await expect(page).toHaveURL(/\/storytelling\/worlds/, { timeout: 15000 });
    await expect(page.getByText("Worlds could not be loaded.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Reload worlds" })).toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // Community route
  // ---------------------------------------------------------------------------

  test("community route renders placeholder surface", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/community");

    await expect(page).toHaveURL(/\/storytelling\/community/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Storytelling Community" })).toBeVisible();
    await expect(page.getByTestId("community-placeholder")).toBeVisible();
    await expect(page.getByText("Community features are coming")).toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // Auth guard — all three routes redirect unauthenticated users
  // ---------------------------------------------------------------------------

  test("stories route redirects unauthenticated users to login", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/storytelling/stories");

    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 15000 });
  });

  test("worlds route redirects unauthenticated users to login", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/storytelling/worlds");

    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 15000 });
  });

  test("community route redirects unauthenticated users to login", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/storytelling/community");

    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 15000 });
  });
});
