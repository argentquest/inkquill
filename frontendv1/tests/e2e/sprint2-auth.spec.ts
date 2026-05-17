import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Sprint 2 auth", () => {
  test("anonymous user is sent to the login experience for protected account access", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/app/account");

    await expect(page).toHaveURL(/\/auth\/login\?next=%2Fapp%2Faccount/, { timeout: 30000 });
    await expect(page.getByRole("heading", { name: "Sign in to continue your work." })).toBeVisible({ timeout: 30000 });
  });

  test("protected account route shows an error state when session bootstrap fails", async ({ page }) => {
    await mockAppApis(page, { session: "session-error" });
    await page.goto("/app/account");

    await expect(page).toHaveURL(/\/auth\/login\?next=%2Fapp%2Faccount/, { timeout: 30000 });
    await expect(page.getByRole("heading", { name: "Sign in to continue your work." })).toBeVisible({ timeout: 30000 });
  });

  test("login success reaches the account landing", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/auth/login?next=%2Fstorytelling%2Faccount");

    await page.locator('input[name="username"]').fill("storymaker");
    await page.locator('input[name="password"]').fill("password123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/storytelling\/account/, { timeout: 20000 });
    await expect(page.getByText("Account summary")).toBeVisible({ timeout: 20000 });
    await expect(page.getByText("Username: storymaker")).toBeVisible({ timeout: 20000 });
  });

  test("login constrains unsafe next targets to the account shell", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/auth/login?next=https%3A%2F%2Fevil.example%2Fsteal");

    await page.locator('input[name="username"]').fill("storymaker");
    await page.locator('input[name="password"]').fill("password123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/storytelling\/account/, { timeout: 20000 });
    await expect(page.url()).not.toContain("evil.example");
  });

  test("login page does not redirect back to itself", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/auth/login?next=%2Fauth%2Flogin");

    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 20000 });
    await expect(page.getByRole("heading", { name: "Sign in to continue your work." })).toBeVisible({ timeout: 30000 });
    await expect(page.getByText("Redirecting to login")).toHaveCount(0);
  });

  test("login error renders clearly", async ({ page }) => {
    await mockAppApis(page, { login: "error" });
    await page.goto("/auth/login");

    await page.locator('input[name="username"]').fill("storymaker");
    await page.locator('input[name="password"]').fill("wrongpass1");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page.getByText("Invalid username or password")).toBeVisible();
  });

  test("register success reaches the preserved protected destination", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/auth/register?next=%2Fstorytelling%2Faccount");

    await page.locator('input[name="username"]').fill("storymaker");
    await page.locator('input[name="email"]').fill("storymaker@example.com");
    await page.locator('input[name="display_name"]').fill("Story Maker");
    await page.locator('input[name="password"]').fill("password123");
    await page.getByRole("checkbox").check();
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page).toHaveURL(/\/storytelling\/account/, { timeout: 20000 });
    await expect(page.getByText("Account summary")).toBeVisible({ timeout: 20000 });
  });

  test("join page pre-fills the invite code from the URL", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/join?code=ab-12 cd");

    await expect(page.locator('input[name="join_code"]')).toHaveValue("AB12CD");
  });

  test("forgot password flow shows success messaging", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/auth/forgot-password");

    await page.locator('input[name="email"]').fill("storymaker@example.com");
    await page.getByRole("button", { name: "Send reset link" }).click();

    await expect(page.getByText("Reset email requested", { exact: true })).toBeVisible({ timeout: 20000 });
  });

  test("reset password flow accepts token and shows success messaging", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/auth/reset-password?token=valid-token");

    await page.locator('input[name="password"]').fill("newpassword123");
    await page.locator('input[name="confirmPassword"]').fill("newpassword123");
    await page.getByRole("button", { name: "Reset password" }).click();

    await expect(page.getByText("Password reset complete")).toBeVisible({ timeout: 20000 });
  });

  test("logout from the shell returns the user to login", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/app/account");

    await page.getByRole("button", { name: /Story Maker/ }).click();
    await expect(page.getByText("Log out")).toBeVisible();
    await page.getByText("Log out").click({ force: true });

    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 30000 });
    await expect(page.getByRole("heading", { name: "Sign in to continue your work." })).toBeVisible({ timeout: 30000 });
  });

  test("google sign-in entry point stays hidden for non-admin users", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/auth/login");

    await expect(page.getByRole("link", { name: "Continue with Google" })).toHaveCount(0);
    await expect(page.getByText("Dev · Quick login")).toHaveCount(0);
  });
});
