import { expect, test, type Page } from "@playwright/test";

const liveAuthEnabled = process.env.PLAYWRIGHT_LIVE_AUTH === "1";
const adminUsername = process.env.PLAYWRIGHT_ADMIN_USERNAME ?? "admin";
const adminPassword = process.env.PLAYWRIGHT_ADMIN_PASSWORD ?? "password123";

async function login(page: Page, username: string, password: string) {
  await page.goto("/auth/login?next=%2Fstorytelling%2Faccount");
  await page.getByLabel("Username").fill(username);
  await page.locator('input[name="password"]').fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
}

async function logout(page: Page, menuLabel: string) {
  await page.getByRole("button", { name: menuLabel, exact: true }).click();
  await page.getByRole("menuitem", { name: "Log out" }).click();
}

test.describe("Live auth accounts", () => {
  test.skip(!liveAuthEnabled, "Set PLAYWRIGHT_LIVE_AUTH=1 to run real backend auth coverage.");

  test("seeded admin can log in through the React app", async ({ page }) => {
    await login(page, adminUsername, adminPassword);

    await expect(page).toHaveURL(/\/storytelling\/account/, { timeout: 30000 });
    await expect(page.getByText("Account summary")).toBeVisible({ timeout: 30000 });
    await expect(page.getByText(`Username: ${adminUsername}`)).toBeVisible({ timeout: 30000 });
  });

  test("freshly registered user can log in after account creation", async ({ page }) => {
    const suffix = `${Date.now()}`;
    const username = `playwright_${suffix}`;
    const email = `playwright_${suffix}@example.com`;
    const password = "password123";
    const displayName = `Playwright ${suffix}`;

    await page.goto("/auth/register?next=%2Fstorytelling%2Faccount");
    await page.getByLabel("Username").fill(username);
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Display name").fill(displayName);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole("checkbox").check();
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page).toHaveURL(/\/storytelling\/account/, { timeout: 30000 });
    await expect(page.getByText("Account summary")).toBeVisible({ timeout: 30000 });
    await expect(page.getByText(`Username: ${username}`)).toBeVisible({ timeout: 30000 });

    await logout(page, displayName);
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 30000 });

    await login(page, username, password);
    await expect(page).toHaveURL(/\/storytelling\/account/, { timeout: 30000 });
    await expect(page.getByText("Account summary")).toBeVisible({ timeout: 30000 });
    await expect(page.getByText(`Username: ${username}`)).toBeVisible({ timeout: 30000 });
  });
});
