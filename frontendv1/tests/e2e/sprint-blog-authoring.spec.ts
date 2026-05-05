import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Blog authoring surface", () => {
  test("storytelling blog dashboard loads posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog");

    await expect(page).toHaveURL(/\/storytelling\/blog/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Blog", exact: true })).toBeVisible();
    await expect(page.getByText("My First Blog Post")).toBeVisible();
    await expect(page.getByText("Writing Tips for Fantasy")).toBeVisible();
  });

  test("care circle blog dashboard loads posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/blog");

    await expect(page).toHaveURL(/\/care-circle-family\/blog/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Blog", exact: true })).toBeVisible();
    await expect(page.getByText("My First Blog Post")).toBeVisible();
    await expect(page.getByText("Writing Tips for Fantasy")).toBeVisible();
  });

  test("storytelling blog dashboard shows empty state", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated", authorBlogPosts: "empty" });
    await page.goto("/storytelling/blog");

    await expect(page).toHaveURL(/\/storytelling\/blog/, { timeout: 15000 });
    await expect(page.getByTestId("blog-empty-state")).toBeVisible();
    await expect(page.getByText("No blog posts yet")).toBeVisible();
  });

  test("storytelling new post page loads", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog/new");

    await expect(page).toHaveURL(/\/storytelling\/blog\/new/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "New post" })).toBeVisible();
    await expect(page.getByTestId("post-title-input")).toBeVisible();
    await expect(page.getByTestId("post-content-input")).toBeVisible();
  });

  test("care circle new post page loads", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/blog/new");

    await expect(page).toHaveURL(/\/care-circle-family\/blog\/new/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "New post" })).toBeVisible();
    await expect(page.getByTestId("post-title-input")).toBeVisible();
    await expect(page.getByTestId("post-content-input")).toBeVisible();
  });

  test("storytelling media library loads", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog/media");

    await expect(page).toHaveURL(/\/storytelling\/blog\/media/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Media Library" })).toBeVisible();
    await expect(page.getByTestId("media-grid")).toBeVisible();
  });

  test("care circle media library loads", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/blog/media");

    await expect(page).toHaveURL(/\/care-circle-family\/blog\/media/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Media Library" })).toBeVisible();
    await expect(page.getByTestId("media-grid")).toBeVisible();
  });
});
