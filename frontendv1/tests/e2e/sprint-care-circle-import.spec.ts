import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Care Circle DailyNewsletter import", () => {
  test("family patient profiles render on the protected family route", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients");

    await expect(page.getByRole("heading", { name: "Patient profiles now behave like managed family-side care records." })).toBeVisible();
    await expect(page.getByText("Rose Ellis")).toBeVisible();
    await expect(page.getByText("Arthur Bloom")).toBeVisible();
    await expect(page.getByText("Patient sign-in", { exact: false })).toHaveCount(0);
  });

  test("patient picture sign-in reaches the calm daily highlights view", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/login");

    await page.getByRole("button", { name: "Sun" }).click();
    await page.getByRole("button", { name: "Dog" }).click();
    await page.getByRole("button", { name: "House" }).click();
    await page.getByRole("button", { name: "Continue" }).click();

    await expect(page).toHaveURL(/\/care-circle-patient\/home\?patient=1/);
    await expect(page.getByRole("heading", { name: "Your day is ready." })).toBeVisible();
    await expect(page.getByText("Family hello")).toBeVisible();
    await expect(page.getByText("Memory lane")).toBeVisible();
  });
});
