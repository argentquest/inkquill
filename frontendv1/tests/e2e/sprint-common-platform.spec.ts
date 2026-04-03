import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Sprint common platform routes", () => {
  test("anonymous users are redirected to login for protected storytelling access", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/storytelling");

    await expect(page).toHaveURL(/\/auth\/login\?next=%2Fstorytelling/, { timeout: 30000 });
    await expect(page.getByRole("heading", { name: "Sign in to continue your work." })).toBeVisible({ timeout: 30000 });
  });

  test("authenticated storytelling access resolves the shared shell and realtime state", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling");

    await expect(page.getByRole("heading", { name: "Creative authoring remains a separate app surface." })).toBeVisible({ timeout: 30000 });
    await expect(page.getByText("User scope")).toBeVisible();
    await expect(page.getByText("Realtime ready")).toBeVisible();

    await page.context().setOffline(true);
    await expect(page.getByText("Realtime offline")).toBeVisible({ timeout: 10000 });
    await page.context().setOffline(false);
  });

  test("membership denial resolves to an explicit access-denied route", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family?membership=denied");

    await expect(page).toHaveURL(/\/access-denied\?surface=care-circle-family/, { timeout: 30000 });
    await expect(page.getByRole("heading", { name: "This application surface is not available for the current account." })).toBeVisible({
      timeout: 30000
    });
  });

  test("patient direct-entry remains reachable without authentication", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient");

    await expect(page).toHaveURL(/\/care-circle-patient/, { timeout: 30000 });
    await expect(page.getByRole("heading", { name: "Direct-entry patient access stays separate from family and storytelling." })).toBeVisible({
      timeout: 30000
    });
    await expect(page.getByText("Patient scope")).toBeVisible();
  });
});
