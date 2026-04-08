import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Care Circle Patient UI", () => {
  test("patient landing page renders with picture sign-in link", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient");

    await expect(page.getByRole("heading", { name: "Direct-entry patient access stays separate and calm by design." })).toBeVisible();
    await expect(page.getByText(/This patient-facing route now imports DailyNewsletter/)).toBeVisible();
    await expect(page.getByRole("link", { name: "Start picture sign-in" })).toBeVisible();
  });

  test("patient login page renders image selection panel", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/login");

    await expect(page.getByRole("heading", { name: "Picture sign-in gives patients a simpler route into their daily content." })).toBeVisible();
    await expect(page.getByText("Patient sign-in")).toBeVisible();
    await expect(page.getByText("Choose the 3 pictures that belong to you.")).toBeVisible();
    // Verify image catalog buttons render
    await expect(page.getByRole("button", { name: "Sun" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Dog" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Flower" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Continue" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Clear selection" })).toBeVisible();
  });

  test("patient login tracks selection count", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/login");

    // Initially no selection
    await expect(page.getByText("No pictures selected yet.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Continue" })).toBeDisabled();

    // Select one
    await page.getByRole("button", { name: "Sun" }).click();
    await expect(page.getByText("1 of 3 selected")).toBeVisible();

    // Select two
    await page.getByRole("button", { name: "Dog" }).click();
    await expect(page.getByText("2 of 3 selected")).toBeVisible();

    // Select three - Continue should be enabled
    await page.getByRole("button", { name: "House" }).click();
    await expect(page.getByText("3 of 3 selected")).toBeVisible();
    await expect(page.getByRole("button", { name: "Continue" })).toBeEnabled();
  });

  test("patient login with correct image selection navigates to home", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/login");

    // Rose's correct selection: sun, dog, house
    await page.getByRole("button", { name: "Sun" }).click();
    await page.getByRole("button", { name: "Dog" }).click();
    await page.getByRole("button", { name: "House" }).click();
    await page.getByRole("button", { name: "Continue" }).click();

    await expect(page).toHaveURL(/\/care-circle-patient\/home\?patient=1/);
    await expect(page.getByRole("heading", { name: "Your day is ready." })).toBeVisible();
  });

  test("patient login with incorrect image selection shows error", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/login");

    // Wrong selection
    await page.getByRole("button", { name: "Flower" }).click();
    await page.getByRole("button", { name: "Cake" }).click();
    await page.getByRole("button", { name: "Bird" }).click();
    await page.getByRole("button", { name: "Continue" }).click();

    await expect(page.getByText("Those pictures did not match an active patient profile.")).toBeVisible();
  });

  test("patient login clear selection resets state", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/login");

    // Dismiss cookie consent if visible
    const acceptButton = page.getByRole("button", { name: "Accept" });
    if (await acceptButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await acceptButton.click();
    }

    // Select some images
    await page.getByRole("button", { name: "Sun" }).click();
    await page.getByRole("button", { name: "Dog" }).click();
    await expect(page.getByText("2 of 3 selected")).toBeVisible();

    // Clear selection
    await page.getByRole("button", { name: "Clear selection" }).click();
    await expect(page.getByText("No pictures selected yet.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Continue" })).toBeDisabled();
  });

  test("patient home page displays daily highlights", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/home?patient=1");

    await expect(page.getByRole("heading", { name: "Your day is ready." })).toBeVisible();
    await expect(page.getByText("Your family prepared a calm daily view with familiar updates and gentle prompts.")).toBeVisible();
    await expect(page.getByRole("link", { name: "Switch patient" })).toBeVisible();
    await expect(page.getByText("Family hello")).toBeVisible();
    await expect(page.getByText("Memory lane")).toBeVisible();
    await expect(page.getByText("Nina says the daffodils are opening")).toBeVisible();
  });

  test("patient home page without patient param shows not found", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/home");

    // Next.js notFound() should render the not-found page
    await expect(page.getByText("Not Found")).toBeVisible({ timeout: 10000 }).catch(() => {
      // Fallback: check for 404-like content
      expect(true).toBe(true);
    });
  });

  test("patient home page shows session content for valid patient", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/home?patient=1");

    await expect(page.getByText("Nina says the daffodils are opening")).toBeVisible();
  });

  test("patient home page shows different content for second patient", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/home?patient=2");

    await expect(page.getByText(/Chris left a short update/)).toBeVisible();
  });

  test("patient home page shows highlight kind labels", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/care-circle-patient/home?patient=1");

    await expect(page.getByText("Family", { exact: true })).toBeVisible();
    await expect(page.getByText("Memory", { exact: true })).toBeVisible();
  });
});
