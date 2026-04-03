import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Sprint 1 shell", () => {
  test("home route renders editorial shell and account entry", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Editorial shell, not a generic dashboard." })).toBeVisible();
    await expect(page.getByRole("link", { name: "Open App Shell" })).toBeVisible();
    await expect(page.getByRole("button", { name: /Loading balance|25\.75 Coins/ })).toBeVisible();
  });

  test("public route renders empty-state shell", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/public");

    await expect(page.getByRole("heading", { name: "Public-facing routes keep the same voice without copying the app workspace." })).toBeVisible();
    await expect(page.getByRole("heading", { name: "This surface is intentionally sparse in Sprint 1." })).toBeVisible();
  });

  test("account route supports authenticated shell state", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/app/account");

    await expect(page.getByRole("heading", { name: "Welcome back, Story Maker." })).toBeVisible();
    await expect(page.getByText("Username: storymaker")).toBeVisible();
    await expect(page.getByText("Admin: Yes")).toBeVisible();
    await expect(page.locator("article").filter({ hasText: "Coin balance" }).getByRole("heading", { name: "25.75" })).toBeVisible();
  });

  test("maintenance mode shows banner and workspace gate", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated", maintenance: "on" });
    await page.goto("/app/account");

    await expect(page.getByText("Maintenance Mode")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Maintenance is active" })).toBeVisible();
    await expect(page.getByText("Planned maintenance window", { exact: true })).toBeVisible();
  });

  test("theme toggle and cookie consent persist across reload", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/");

    await page.getByRole("button", { name: "Accept" }).click();
    await expect(page.getByText("Cookie Consent")).toHaveCount(0);

    await page.getByRole("button", { name: "Night Mode" }).click();
    await expect(page.getByRole("button", { name: "Day Mode" })).toBeVisible();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");

    await page.reload();

    await expect(page.getByRole("button", { name: "Day Mode" })).toBeVisible();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(page.getByText("Cookie Consent")).toHaveCount(0);
  });

  test("failed balance request surfaces warning toast", async ({ page }) => {
    await mockAppApis(page, { balance: "error" });
    await page.goto("/");

    await expect(page.getByText("Balance unavailable")).toBeVisible();
    await expect(page.getByText("The shell will continue without live balance data.")).toBeVisible();
  });

  test("toast notifications can be dismissed", async ({ page }) => {
    await mockAppApis(page, { balance: "error" });
    await page.goto("/");

    await expect(page.getByText("Balance unavailable")).toBeVisible();
    await page.getByRole("button", { name: "Dismiss notification" }).click();
    await expect(page.getByText("Balance unavailable")).toHaveCount(0);
  });
});
