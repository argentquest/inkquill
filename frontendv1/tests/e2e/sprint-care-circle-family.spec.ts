import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Care Circle Family UI", () => {
  test("family landing page renders with navigation links", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family");

    await expect(page.getByRole("heading", { name: "Family-side care workflows now sit on imported patient and provider foundations." })).toBeVisible();
    await expect(page.getByText(/Care Circle remains a separate application/)).toBeVisible();
    await expect(page.getByRole("link", { name: "Open patient profiles" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Preview patient sign-in" })).toBeVisible();
  });

  test("family patients page renders patient list", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients");

    await expect(page.getByRole("heading", { name: "Patient profiles now behave like managed family-side care records." })).toBeVisible();
    await expect(page.getByText("Rose Ellis")).toBeVisible();
    await expect(page.getByText("Arthur Bloom")).toBeVisible();
    await expect(page.getByText("moderate")).toBeVisible();
    await expect(page.getByText("mild")).toBeVisible();
    await expect(page.getByText("active", { exact: true })).toBeVisible();
    await expect(page.getByText("inactive")).toBeVisible();
  });

  test("family patients page shows patient preferences", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients");

    // Rose's preferences
    await expect(page.getByText("1950s music")).toBeVisible();
    await expect(page.getByText("family photos")).toBeVisible();
    await expect(page.getByText("tea and biscuits")).toBeVisible();
    await expect(page.getByText("gardening")).toBeVisible();
  });

  test("family patients page shows family circle members", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients");

    await expect(page.getByText("Family circle: Nina, Paul, Maggie")).toBeVisible();
  });

  test("family patients page allows navigation to patient detail", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients");

    await page.getByRole("link", { name: "Edit" }).first().click();
    await expect(page).toHaveURL(/\/care-circle-family\/patients\/1/);
  });

  test("family patient detail page renders patient profile", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/1");

    await expect(page.getByRole("heading", { name: "Friend profile" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Back to friends" })).toBeVisible();
    await expect(page.getByText("Profile summary")).toBeVisible();
  });

  test("family patient detail page shows patient identity", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/1");

    await expect(page.getByRole("heading", { name: "Profile summary" })).toBeVisible();
    await expect(page.getByText("Story Maker household")).toBeVisible();
  });

  test("family patient detail page shows care stage and access state", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/1");

    await expect(page.getByText("moderate")).toBeVisible();
    await expect(page.getByText("active")).toBeVisible();
  });

  test("family patient detail page shows delivery schedule", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/1");

    await expect(page.getByText("08:30")).toBeVisible();
    await expect(page.getByText("Mon, Wed, Fri, Sun")).toBeVisible();
    await expect(page.getByText("America/Chicago")).toBeVisible();
  });

  test("family patient detail page shows image sign-in keys", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/1");

    await expect(page.getByText("Image sign-in")).toBeVisible();
    await expect(page.getByText("sun", { exact: true })).toBeVisible();
    await expect(page.getByText("dog", { exact: true })).toBeVisible();
    await expect(page.getByText("house", { exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Preview patient sign-in" })).toBeVisible();
  });

  test("family patient detail page shows patient preferences", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/1");

    await expect(page.getByText("Patient preferences")).toBeVisible();
    await expect(page.getByText("1950s music")).toBeVisible();
    await expect(page.getByText("family photos")).toBeVisible();
    await expect(page.getByText("tea and biscuits")).toBeVisible();
    await expect(page.getByText("gardening")).toBeVisible();
  });

  test("family patient detail page shows family circle", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/1");

    await expect(page.getByText("Family circle: Nina, Paul, Maggie.")).toBeVisible();
  });

  test("family patient detail page allows provider selection per patient", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/1?edit=1");

    await expect(page.getByRole("heading", { name: "Provider selection" })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Weather/ })).toBeVisible();
    await expect(page.getByText("Daily Joy")).toBeVisible();

    await expect(page.getByRole("button", { name: "Enabled" }).first()).toBeVisible();
    await page.getByRole("button", { name: "Disabled" }).click();
    await expect(page.getByRole("button", { name: "Enabled" }).nth(1)).toBeVisible();
  });

  test("family patient detail page shows second patient data", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/patients/2");

    await expect(page.getByRole("heading", { name: "Profile summary" })).toBeVisible();
    await expect(page.getByText("Story Maker household")).toBeVisible();
    await expect(page.getByText("mild")).toBeVisible();
    await expect(page.getByText("inactive")).toBeVisible();
    await expect(page.getByText("America/New_York")).toBeVisible();
    await expect(page.getByText("09:15")).toBeVisible();
    await expect(page.getByText("Tue, Thu, Sat")).toBeVisible();
    await expect(page.getByText("local history")).toBeVisible();
    await expect(page.getByText("jazz")).toBeVisible();
    await expect(page.getByText("crosswords")).toBeVisible();
    await expect(page.getByText("Family circle: Janet, Chris.")).toBeVisible();
  });

  test("family providers page renders provider catalog", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/providers");

    await expect(page.getByRole("heading", { name: "Content Providers" })).toBeVisible();
    await expect(page.getByText("Review and configure the content providers available")).toBeVisible();
  });

  test("family provider detail page loads", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/providers/weather");

    await expect(page.getByRole("link", { name: "Back to Providers" })).toBeVisible({ timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Patient mapping" })).toBeVisible();
    await expect(page.getByText("Rose Ellis")).toBeVisible();
    await expect(page.getByText("Arthur Bloom")).toBeVisible();
    await expect(page.getByRole("button", { name: "Enabled" }).first()).toBeVisible();
  });

  test("family admin template studio loads GrapesJS editor controls", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/admin/template-studio?provider=weather&theme=classic");

    await expect(page.getByRole("heading", { name: "Care Circle Provider Templates" })).toBeVisible();
    await expect(page.getByText("Edit provider `default.html` files with GrapesJS")).toBeVisible();
    await expect(page.getByRole("heading", { name: /Weather/ })).toBeVisible();
    await expect(page.getByText("Shared theme loaded: classic")).toBeVisible({ timeout: 15000 });
    await expect(page.getByRole("button", { name: "Save template" })).toBeVisible();
  });

  test("family admin scheduler console renders inside the main UI", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/admin/scheduler");

    await expect(page.getByRole("heading", { name: "Scheduler Console" })).toBeVisible();
    await expect(page.getByText("Provider Output Pre-cache")).toBeVisible();
    await expect(page.getByText("Daily Session Pre-generation")).toBeVisible();
    await expect(page.getByRole("button", { name: "Run now" }).first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Save cron" }).first()).toBeVisible();
    await expect(page.getByRole("heading", { name: "Loaded jobs" })).toBeVisible();
  });

  test("pages without custom help still get a route-aware help button", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/admin");

    const helpButton = page.getByRole("button", { name: "Open help" });
    await expect(helpButton).toBeVisible();
    await helpButton.click();

    await expect(page.getByRole("heading", { name: "Admin Dashboard Help" })).toBeVisible();
    await expect(page.getByText("Manage platform settings, users, and system configuration.")).toBeVisible();
  });

  test("buttons and form fields expose tooltip guidance", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/account/edit");

    await expect(page.getByRole("button", { name: "Save profile" })).toHaveAttribute("title", "Save profile");
    await expect(page.getByRole("button", { name: "Cancel" })).toHaveAttribute("title", "Cancel");
    await expect(page.getByLabel("Display name")).toHaveAttribute("title", /Display name/);
    await expect(page.getByLabel("Username")).toHaveAttribute("title", /Username/);
    await expect(page.getByLabel("Email")).toHaveAttribute("title", /Email/);
  });

  test("family admin families page requires explicit delete confirmation and removes the family", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/admin/families");

    await expect(page.getByRole("heading", { name: "All families" })).toBeVisible();
    await expect(page.getByText("Story Maker household")).toBeVisible();

    await page.getByRole("button", { name: "Delete..." }).first().click();

    await expect(page.getByRole("heading", { name: "Story Maker household" })).toBeVisible();
    await expect(page.getByText("This permanently removes the family, patient profiles, memberships, and related Care Circle data.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Delete Story Maker household" })).toBeVisible();

    await page.getByRole("button", { name: "Delete Story Maker household" }).click();

    await expect(page.getByText("Story Maker household")).not.toBeVisible();
    await expect(page.getByText("Arthur's Circle")).toBeVisible();
    await expect(page.getByText("The family and all its data have been removed.")).toBeVisible();
  });

  test("family events page loads", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/events");

    await expect(page).toHaveURL(/\/care-circle-family\/events/, { timeout: 15000 });
    await expect(page.getByTestId("care-circle-activity-feed")).toBeVisible();
    await expect(page.getByText("Daily content generated")).toBeVisible();
    await expect(page.getByText("Provider fallback used")).toBeVisible();
    await expect(page.getByText("Rose Ellis")).toBeVisible();
  });

  test("family media library page loads", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/media");

    await expect(page).toHaveURL(/\/care-circle-family\/media/, { timeout: 15000 });
    await expect(page.getByText("Upload family photos for Care Circle prompts")).toBeVisible();
    await expect(page.getByTestId("care-circle-media-grid")).toBeVisible();
    await expect(page.getByText("rose-porch.jpg")).toBeVisible();
    await expect(page.getByText("Prompt-ready crops")).toBeVisible();
  });

  test("family media library allows upload and delete", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/media");

    await page.getByTestId("care-circle-media-input").setInputFiles({
      name: "porch-memory.jpg",
      mimeType: "image/jpeg",
      buffer: Buffer.from("fake-image"),
    });

    await expect(page.getByText("Photo uploaded")).toBeVisible();
    await expect(page.getByText("upload-2.jpg")).toBeVisible();

    await page.getByRole("button", { name: "Delete upload-2.jpg" }).click();
    await expect(page.getByText("Photo removed")).toBeVisible();
    await expect(page.getByText("upload-2.jpg")).not.toBeVisible();
  });

  test("family media library shows empty state when no media exists", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/blog/media/list", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }),
      });
    });
    await page.goto("/care-circle-family/media");

    await expect(page).toHaveURL(/\/care-circle-family\/media/, { timeout: 15000 });
    await expect(page.getByText("No media uploaded yet")).toBeVisible();
    await expect(page.getByRole("button", { name: "Upload photos" })).toBeVisible();
  });

  test("family media library shows error state when list API fails", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/blog/media/list", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false, error: { message: "Storage unavailable" } }),
      });
    });
    await page.goto("/care-circle-family/media");

    await expect(page).toHaveURL(/\/care-circle-family\/media/, { timeout: 15000 });
    await expect(page.getByText("Media library unavailable")).toBeVisible();
    await expect(page.getByRole("button", { name: "Reload library" })).toBeVisible();
  });

  test("owner account page shows the join code and can send an invite email", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/account");

    await expect(page.getByRole("heading", { name: "Share your join code or email an invite." })).toBeVisible();
    await expect(page.getByText("STM111")).toBeVisible();
    await expect(page.getByText("Active members")).toBeVisible();
    await expect(page.getByText("Pending requests")).toBeVisible();

    await page.getByLabel("Invite by email").fill("new.member@example.com");
    await page.getByRole("button", { name: "Send invite email" }).click();

    await expect(page.getByText("An invite email was sent to new.member@example.com.")).toBeVisible();
  });
});
