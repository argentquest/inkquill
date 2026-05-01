import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Admin hub", () => {
  test("admin hub loads with section cards", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin");

    await expect(page).toHaveURL(/\/admin/, { timeout: 15000 });
    await expect(page.getByTestId("admin-hub-grid")).toBeVisible();
    await expect(page.getByTestId("admin-hub-card").first()).toBeVisible();
  });

  test("admin hub shows expected section links", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin");

    await expect(page.getByRole("link", { name: /Users/ })).toBeVisible();
    await expect(page.getByRole("link", { name: /Billing/ })).toBeVisible();
    await expect(page.getByRole("link", { name: /CTA/ })).toBeVisible();
    await expect(page.getByRole("link", { name: /Maintenance/ })).toBeVisible();
  });

  test("admin hub redirects when not authenticated", async ({ page }) => {
    await mockAppApis(page, { session: "anonymous" });
    await page.goto("/admin");

    await expect(page).not.toHaveURL(/\/admin$/, { timeout: 15000 });
  });
});

test.describe("Admin users", () => {
  test("admin users page loads user table", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/users");

    await expect(page.getByTestId("admin-users-table")).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId("admin-user-row").first()).toBeVisible();
  });

  test("admin users shows usernames", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/users");

    await expect(page.getByText("storymaker")).toBeVisible();
    await expect(page.getByText("alice")).toBeVisible();
    await expect(page.getByText("bobwriter")).toBeVisible();
  });

  test("admin users shows active/inactive status badges", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/users");

    await expect(page.getByTestId("user-status-badge").first()).toBeVisible();
  });

  test("admin users toggle-active button is present", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/users");

    await expect(page.getByTestId("toggle-active-button").first()).toBeVisible();
  });

  test("admin users toggle-active fires and refreshes", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/users");

    await page.getByTestId("toggle-active-button").first().click();
    // No error state should appear
    await expect(page.getByTestId("users-error")).not.toBeVisible();
  });

  test("admin users auth guard redirects when not authenticated", async ({ page }) => {
    await mockAppApis(page, { session: "anonymous" });
    await page.goto("/admin/users");

    await expect(page).not.toHaveURL(/\/admin\/users$/, { timeout: 15000 });
  });
});

test.describe("Admin billing", () => {
  test("admin billing page loads stats", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/billing");

    await expect(page.getByTestId("billing-stats")).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId("billing-stat-card").first()).toBeVisible();
  });

  test("admin billing shows transaction list", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/billing");

    await expect(page.getByTestId("transactions-list")).toBeVisible({ timeout: 12000 });
    await expect(page.getByTestId("transaction-row").first()).toBeVisible();
  });

  test("admin billing shows manual credit adjustment form", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/billing");

    await expect(page.getByTestId("adjust-user-id")).toBeVisible();
    await expect(page.getByTestId("adjust-amount")).toBeVisible();
    await expect(page.getByTestId("adjust-desc")).toBeVisible();
  });

  test("admin billing adjust credits shows success", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/billing");

    await page.getByTestId("adjust-user-id").fill("8");
    await page.getByTestId("adjust-amount").fill("100");
    await page.getByTestId("adjust-desc").fill("Test adjustment");
    await page.getByRole("button", { name: "Adjust credits" }).click();

    await expect(page.getByTestId("adjust-success")).toBeVisible({ timeout: 8000 });
  });

  test("admin billing auth guard redirects when not authenticated", async ({ page }) => {
    await mockAppApis(page, { session: "anonymous" });
    await page.goto("/admin/billing");

    await expect(page).not.toHaveURL(/\/admin\/billing$/, { timeout: 15000 });
  });
});

test.describe("Admin maintenance", () => {
  test("admin maintenance page loads with status", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/maintenance");

    await expect(page.getByTestId("maintenance-status-label")).toBeVisible({ timeout: 15000 });
  });

  test("admin maintenance shows site is live when off", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated", maintenance: "off" });
    await page.goto("/admin/maintenance");

    await expect(page.getByText("Site is live")).toBeVisible({ timeout: 12000 });
    await expect(page.getByTestId("enable-maintenance-button")).toBeVisible();
  });

  test("admin maintenance enable button is present", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/maintenance");

    await expect(page.getByTestId("maintenance-message-input")).toBeVisible();
    await expect(page.getByTestId("maintenance-duration-input")).toBeVisible();
    await expect(page.getByTestId("enable-maintenance-button")).toBeVisible();
  });

  test("admin maintenance auth guard redirects when not authenticated", async ({ page }) => {
    await mockAppApis(page, { session: "anonymous" });
    await page.goto("/admin/maintenance");

    await expect(page).not.toHaveURL(/\/admin\/maintenance$/, { timeout: 15000 });
  });
});

test.describe("Admin CTA", () => {
  test("admin CTA page loads list", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/cta");

    await expect(page.getByTestId("cta-list")).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId("cta-row").first()).toBeVisible();
  });

  test("admin CTA shows CTA titles", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/cta");

    await expect(page.getByText("Join the Community")).toBeVisible();
    await expect(page.getByText("Upgrade Your Plan")).toBeVisible();
  });

  test("admin CTA shows status badges", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/cta");

    await expect(page.getByTestId("cta-status-badge").first()).toBeVisible();
  });

  test("admin CTA toggle-active button is present", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/cta");

    await expect(page.getByTestId("toggle-cta-button").first()).toBeVisible();
  });

  test("admin CTA delete button is present", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/admin/cta");

    await expect(page.getByTestId("delete-cta-button").first()).toBeVisible();
  });

  test("admin CTA shows empty state when no CTAs", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/admin/cta-content**", async (route) => {
      if (route.request().method() === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: [] }) });
      } else {
        await route.fallback();
      }
    });
    await page.goto("/admin/cta");

    await expect(page.getByTestId("cta-empty")).toBeVisible({ timeout: 8000 });
  });

  test("admin CTA auth guard redirects when not authenticated", async ({ page }) => {
    await mockAppApis(page, { session: "anonymous" });
    await page.goto("/admin/cta");

    await expect(page).not.toHaveURL(/\/admin\/cta$/, { timeout: 15000 });
  });
});
