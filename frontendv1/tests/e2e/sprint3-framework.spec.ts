import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Sprint 3 framework routes", () => {
  test("account edit saves profile changes into the shared shell session", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/app/account/edit");

    await page.getByLabel("Display name").fill("Draft Cartographer");
    await page.getByRole("button", { name: "Save profile" }).click();

    await expect(page).toHaveURL(/\/storytelling\/account/, { timeout: 20000 });
    await expect(page.getByText("Profile updated")).toBeVisible({ timeout: 20000 });
    await expect(page.getByRole("heading", { name: "Draft Cartographer" })).toBeVisible({ timeout: 20000 });
  });

  test("billing route loads dashboard data", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/app/billing");

    await expect(page).toHaveURL(/\/storytelling\/billing/, { timeout: 30000 });
    await expect(page.getByRole("heading", { name: "Your balance, packages, and transaction history live in one route." })).toBeVisible({ timeout: 20000 });
    await expect(page.getByRole("heading", { name: "120" })).toBeVisible();
    await expect(page.getByRole("table", { name: "Billing transactions" })).toBeVisible();
    await expect(page.getByText("Starter")).toBeVisible();
  });

  test("referrals route loads stats and history", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/app/referrals");

    await expect(page).toHaveURL(/\/storytelling\/referrals/, { timeout: 30000 });
    await expect(page.getByText("Track invitations, conversions, and earned coins from one route.")).toBeVisible({ timeout: 20000 });
    await expect(page.getByText("50%")).toBeVisible();
    await expect(page.getByRole("table", { name: "Referral history" })).toBeVisible();
  });

  test("onboarding route shows question preview and pending state", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/app/onboarding");

    await expect(page).toHaveURL(/\/storytelling\/onboarding/, { timeout: 30000 });
    await expect(page.getByText("Set the direction for your writing workspace.")).toBeVisible({ timeout: 20000 });
    await expect(page.getByText("Welcome! Let's get to know you better")).toBeVisible();
    await expect(page.getByText("No personalized insights yet.")).toBeVisible();
  });

  test("public info routes are reachable on the shared shell", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/help");

    await expect(page.getByRole("heading", { name: "Help is part of the framework, not an afterthought." })).toBeVisible({ timeout: 20000 });

    await page.goto("/privacy");
    await expect(page.getByRole("heading", { name: "Privacy terms can live inside the new route system from the start." })).toBeVisible({ timeout: 20000 });
  });
});
