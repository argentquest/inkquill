import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

const authorBlogPostsSeed = [
  {
    id: 201,
    title: "My First Blog Post",
    slug: "my-first-blog-post",
    content: "This is the content of my first blog post.",
    excerpt: "An introductory post.",
    featured_image_url: null,
    status: "draft",
    author_id: 7,
    view_count: 0,
    like_count: 0,
    comment_count: 0,
    published_at: null,
    created_at: "2026-04-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 202,
    title: "Writing Tips for Fantasy",
    slug: "writing-tips-fantasy",
    content: "Here are my top five writing tips for fantasy authors.",
    excerpt: "Five tips for fantasy writing.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 42,
    like_count: 5,
    comment_count: 2,
    published_at: "2026-04-10T00:00:00Z",
    created_at: "2026-04-08T00:00:00Z",
    updated_at: "2026-04-10T00:00:00Z",
  },
];

async function mockAuthorBlogPosts(page: any) {
  await page.route("**/api/blog/posts?*", async (route: any) => {
    const url = route.request().url();
    if (url.includes("author_id")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: authorBlogPostsSeed }),
      });
      return;
    }
    await route.fallback();
  });
}

test.describe("Blog authoring surface", () => {
  test("storytelling blog dashboard loads posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await mockAuthorBlogPosts(page);
    await page.goto("/storytelling/blog");

    await expect(page).toHaveURL(/\/storytelling\/blog/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Blog", exact: true })).toBeVisible();
    await expect(page.getByText("My First Blog Post")).toBeVisible();
    await expect(page.getByText("Writing Tips for Fantasy")).toBeVisible();
  });

  test("care circle blog dashboard loads posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await mockAuthorBlogPosts(page);
    await page.goto("/care-circle-family/blog");

    await expect(page).toHaveURL(/\/care-circle-family\/blog/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Blog", exact: true })).toBeVisible();
    await expect(page.getByText("My First Blog Post")).toBeVisible();
    await expect(page.getByText("Writing Tips for Fantasy")).toBeVisible();
  });

  test("storytelling blog dashboard shows empty state", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/blog/posts?*", async (route) => {
      if (route.request().url().includes("author_id")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ success: true, data: [] }),
        });
        return;
      }
      await route.fallback();
    });
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
