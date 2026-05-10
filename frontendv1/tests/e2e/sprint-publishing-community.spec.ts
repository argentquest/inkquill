import { expect, test } from "@playwright/test";

import { mockAppApis } from "./helpers";

test.describe("Published stories routes", () => {
  test("published stories list loads story cards", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/public/published-stories");

    await expect(page).toHaveURL(/\/public\/published-stories/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Published Stories" })).toBeVisible();
    await expect(page.getByTestId("published-stories-list")).toBeVisible();
    await expect(page.getByText("The Silver Compass — Published")).toBeVisible();
  });

  test("published stories list shows empty state when no stories", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/published-stories/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: { stories: [], total: 0, page: 1, per_page: 20 } }),
      });
    });
    await page.goto("/public/published-stories");

    await expect(page).toHaveURL(/\/public\/published-stories/, { timeout: 15000 });
    await expect(page.getByTestId("published-stories-empty-state")).toBeVisible();
    await expect(page.getByText("No published stories yet")).toBeVisible();
  });

  test("published stories list shows error state when API fails", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/published-stories/**", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false }),
      });
    });
    await page.goto("/public/published-stories");

    await expect(page).toHaveURL(/\/public\/published-stories/, { timeout: 15000 });
    await expect(page.getByText("Published stories could not be loaded.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Reload stories" })).toBeVisible();
  });

  test("published story reader loads story detail", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/public/stories/101");

    await expect(page).toHaveURL(/\/public\/stories\/101/, { timeout: 15000 });
    await expect(page.getByTestId("story-reader")).toBeVisible();
    await expect(page.getByText("The Silver Compass — Published")).toBeVisible();
    await expect(page.getByTestId("story-reader").getByText("Story Maker")).toBeVisible();
    await expect(page.getByText("Aethoria")).toBeVisible();
  });

  test("published story reader supports rating, comments, and sharing", async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: { writeText: () => Promise.resolve() },
      });
    });
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/public/stories/101");

    await expect(page.getByTestId("story-rating-controls")).toBeVisible();
    await page.getByRole("button", { name: "Rate story 5 stars" }).click();
    await expect(page.getByText("You rated this story 5 out of 5.")).toBeVisible();

    await page.getByTestId("story-comment-input").fill("Loved the final image in the harbor scene.");
    await page.getByRole("button", { name: "Post comment" }).click();
    await expect(page.getByText("Loved the final image in the harbor scene.")).toBeVisible();

    await page.getByRole("button", { name: "Share link" }).click();
    await expect(page.getByText("The story link has been copied to your clipboard.")).toBeVisible();
  });

  test("published story reader shows error state for unknown story", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/published-stories/999", async (route) => {
      await route.fulfill({ status: 404, contentType: "application/json",
        body: JSON.stringify({ detail: "Published story not found" }) });
    });
    await page.goto("/public/stories/999");

    await expect(page).toHaveURL(/\/public\/stories\/999/, { timeout: 15000 });
    await expect(page.getByText("Story could not be loaded.")).toBeVisible();
  });
});

test.describe("User published stories (storytelling/published)", () => {
  test("shows user's own published stories", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/published");

    await expect(page).toHaveURL(/\/storytelling\/published/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Your Published Stories" })).toBeVisible();
    await expect(page.getByTestId("my-published-list")).toBeVisible();
    await expect(page.getByText("The Silver Compass — Published")).toBeVisible();
  });

  test("shows empty state when user has no published stories", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/published-stories/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: { stories: [], total: 0, page: 1, per_page: 20 } }),
      });
    });
    await page.goto("/storytelling/published");

    await expect(page).toHaveURL(/\/storytelling\/published/, { timeout: 15000 });
    await expect(page.getByTestId("my-published-empty-state")).toBeVisible();
    await expect(page.getByText("No published stories yet")).toBeVisible();
  });

  test("redirects unauthenticated users to login", async ({ page }) => {
    await mockAppApis(page);
    await page.goto("/storytelling/published");

    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 15000 });
  });
});

test.describe("Storytelling community hub", () => {
  test("community hub links public publishing routes together", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/community");

    await expect(page).toHaveURL(/\/storytelling\/community$/, { timeout: 15000 });
    await expect(page.getByTestId("storytelling-community-hub")).toBeVisible();
    await expect(page.getByText("Move from private drafting into public readership.")).toBeVisible();
    await expect(page.getByRole("link", { name: /Published Stories/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Forums/i })).toBeVisible();
    await expect(page.getByTestId("storytelling-community-hub").getByRole("link", { name: "Blog" })).toBeVisible();
    await expect(page.getByRole("link", { name: /Discovery Search/i })).toBeVisible();
  });
});

test.describe("Blog routes", () => {
  test("blog list loads post cards", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/public/blog");

    await expect(page).toHaveURL(/\/public\/blog$/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Blog", exact: true })).toBeVisible();
    await expect(page.getByTestId("blog-list")).toBeVisible();
    await expect(page.getByText("Introducing World Builder 2.0")).toBeVisible();
  });

  test("blog list shows empty state when no posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated", blogPosts: "empty" });
    await page.goto("/public/blog");

    await expect(page).toHaveURL(/\/public\/blog$/, { timeout: 15000 });
    await expect(page.getByTestId("blog-empty-state")).toBeVisible();
    await expect(page.getByText("No posts yet")).toBeVisible();
  });

  test("blog post page loads post content", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/public/blog/introducing-world-builder-2");

    await expect(page).toHaveURL(/\/public\/blog\/introducing-world-builder-2/, { timeout: 15000 });
    await expect(page.getByTestId("blog-post")).toBeVisible();
    await expect(page.getByText("Introducing World Builder 2.0")).toBeVisible();
    await expect(page.getByTestId("blog-post-content")).toBeVisible();
  });

  test("blog post page shows error for unknown slug", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/blog/posts/no-such-post*", async (route) => {
      await route.fulfill({ status: 404, contentType: "application/json",
        body: JSON.stringify({ detail: "Blog post not found" }) });
    });
    await page.goto("/public/blog/no-such-post");

    await expect(page).toHaveURL(/\/public\/blog\/no-such-post/, { timeout: 15000 });
    await expect(page.getByText("Blog post could not be loaded.")).toBeVisible();
  });
});

test.describe("Search route", () => {
  test("search page shows prompt when query is too short", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/public/search");

    await expect(page).toHaveURL(/\/public\/search/, { timeout: 15000 });
    await expect(page.getByTestId("search-prompt")).toBeVisible();
  });

  test("search page shows results for matching query", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/public/search?q=World+Builder");

    await expect(page).toHaveURL(/\/public\/search/, { timeout: 15000 });
    await expect(page.getByTestId("search-results")).toBeVisible();
    await expect(page.getByText("Introducing World Builder 2.0")).toBeVisible();
  });

  test("search page shows no-results state for unmatched query", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/blog/search/**", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }) });
    });
    await page.goto("/public/search?q=xyzzy999");

    await expect(page).toHaveURL(/\/public\/search/, { timeout: 15000 });
    await expect(page.getByTestId("search-no-results")).toBeVisible();
    await expect(page.getByText(/No results for/)).toBeVisible();
  });
});

test.describe("Forum routes", () => {
  test("forums page loads categories and recent threads", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums");

    await expect(page).toHaveURL(/\/community\/forums$/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Forums" })).toBeVisible();
    await expect(page.getByTestId("forum-categories")).toBeVisible();
    await expect(page.getByTestId("forum-categories").getByText("World Building")).toBeVisible();
    await expect(page.getByTestId("forum-categories").getByText("Story Craft")).toBeVisible();
    await expect(page.getByTestId("forum-recent-threads")).toBeVisible();
    await expect(page.getByText("How do you structure a magic system?")).toBeVisible();
  });

  test("forums page shows empty state when no categories", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/forum/categories**", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }) });
    });
    await page.route("**/api/v1/forum/threads**", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }) });
    });
    await page.goto("/community/forums");

    await expect(page).toHaveURL(/\/community\/forums$/, { timeout: 15000 });
    await expect(page.getByTestId("forum-empty-state")).toBeVisible();
    await expect(page.getByText("No forum categories yet")).toBeVisible();
  });

  test("forum thread page loads thread detail and posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/1");

    await expect(page).toHaveURL(/\/community\/forums\/1/, { timeout: 15000 });
    await expect(page.getByTestId("forum-thread")).toBeVisible();
    await expect(page.getByText("How do you structure a magic system?")).toBeVisible();
    await expect(page.getByTestId("thread-posts")).toBeVisible();
    await expect(page.getByText("I always start with the limitations before the powers.")).toBeVisible();
  });

  test("forum thread shows error state for unknown thread", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/forum/threads/999*", async (route) => {
      await route.fulfill({ status: 404, contentType: "application/json",
        body: JSON.stringify({ detail: "Thread not found" }) });
    });
    await page.goto("/community/forums/999");

    await expect(page).toHaveURL(/\/community\/forums\/999/, { timeout: 15000 });
    await expect(page.getByText("Thread could not be loaded.")).toBeVisible();
  });

  test("forum thread page renders reply composer for open thread", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/1");

    await expect(page.getByTestId("reply-composer")).toBeVisible();
    await expect(page.getByTestId("reply-input")).toBeVisible();
    await expect(page.getByRole("button", { name: "Post reply" })).toBeVisible();
  });

  test("forum thread reply composer submits and refreshes posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/1");

    await page.getByTestId("reply-input").fill("Great discussion, adding my thoughts here.");
    await page.getByRole("button", { name: "Post reply" }).click();

    await expect(page.getByRole("button", { name: "Post reply" })).toBeVisible({ timeout: 5000 });
  });

  test("forum thread page shows locked notice for locked thread", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.route("**/api/v1/forum/threads/1*", async (route) => {
      if (route.request().method() !== "GET") { await route.fallback(); return; }
      const lockedThread = {
        id: 1,
        title: "How do you structure a magic system?",
        slug: "magic-system",
        status: "open",
        category_id: 1,
        category_name: "World Building",
        user_id: 7,
        username: "storymaker",
        view_count: 142,
        post_count: 1,
        last_post_at: "2026-04-01T10:00:00Z",
        last_post_by_username: "storymaker",
        is_pinned: false,
        is_locked: true,
        created_at: "2026-04-01T09:00:00Z",
        updated_at: "2026-04-01T10:00:00Z",
        posts: [],
      };
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify({ success: true, data: lockedThread }) });
    });
    await page.goto("/community/forums/1");

    await expect(page.getByTestId("thread-locked-notice")).toBeVisible();
    await expect(page.getByText("This thread is locked.")).toBeVisible();
  });

  test("forums page has new thread link", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums");

    await expect(page.getByTestId("new-thread-link")).toBeVisible();
    await page.getByTestId("new-thread-link").click();
    await expect(page).toHaveURL(/\/community\/forums\/new/, { timeout: 15000 });
  });

  test("new thread page renders form with title, category, and content fields", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/new");

    await expect(page).toHaveURL(/\/community\/forums\/new/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "Start a new thread" })).toBeVisible();
    await expect(page.getByTestId("thread-title-input")).toBeVisible();
    await expect(page.getByTestId("thread-category-select")).toBeVisible();
    await expect(page.getByTestId("thread-content-input")).toBeVisible();
    await expect(page.getByRole("button", { name: "Start thread" })).toBeVisible();
  });

  test("new thread page creates thread and redirects to it", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/new");

    await page.getByTestId("thread-title-input").fill("Best world-building resources?");
    await page.getByTestId("thread-category-select").selectOption({ index: 1 });
    await page.getByTestId("thread-content-input").fill("Looking for recommendations on world-building books and tools.");
    await page.getByRole("button", { name: "Start thread" }).click();

    await expect(page).toHaveURL(/\/community\/forums\/99/, { timeout: 15000 });
    await expect(page.getByTestId("forum-thread")).toBeVisible();
  });

  test("storytelling app home page shows 5 recent forum posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling");

    const section = page.getByTestId("recent-forum-posts");
    await expect(section).toBeVisible();
    await expect(section.getByText("Creating believable political systems")).toBeVisible();
    await expect(section.getByText("Plot twist techniques that actually work")).toBeVisible();
    await expect(section.getByText("Favorite AI prompts for character voice?")).toBeVisible();
    await expect(section.getByText("How do you structure a magic system?")).toBeVisible();
    await expect(section.getByText("Character arcs vs flat characters")).toBeVisible();
  });

  test("care circle family home page shows recent forum posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family");

    const section = page.getByTestId("recent-forum-posts");
    await expect(section).toBeVisible();
    await expect(section.getByText("Best routines for morning care?")).toBeVisible();
    await expect(section.getByText("Photo sharing tips for Memory Lane?")).toBeVisible();
  });

  test("storytelling forum scoped new thread picks storytelling category", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/new?app_source=storytelling");

    await expect(page.getByRole("heading", { name: "Start a new thread" })).toBeVisible();
    await page.getByTestId("thread-title-input").fill("My magic system needs work");
    await page.getByTestId("thread-category-select").selectOption({ label: "World Building" });
    await page.getByTestId("thread-content-input").fill("I am struggling with hard magic rules.");
    await page.getByRole("button", { name: "Start thread" }).click();

    await expect(page).toHaveURL(/\/community\/forums\/99/, { timeout: 15000 });
    await expect(page.getByText("My magic system needs work")).toBeVisible();
  });

  test("care circle forum scoped new thread picks care-circle category", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/new?app_source=care-circle");

    await expect(page.getByRole("heading", { name: "Start a new thread" })).toBeVisible();
    await page.getByTestId("thread-title-input").fill("New caregiver looking for tips");
    await page.getByTestId("thread-category-select").selectOption({ label: "Care Tips & Resources" });
    await page.getByTestId("thread-content-input").fill("What are your best morning routine tips for seniors?");
    await page.getByRole("button", { name: "Start thread" }).click();

    await expect(page).toHaveURL(/\/community\/forums\/99/, { timeout: 15000 });
    await expect(page.getByText("New caregiver looking for tips")).toBeVisible();
  });

  test("storytelling forum thread reply adds a post", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/1");

    await expect(page.getByTestId("reply-composer")).toBeVisible();
    await page.getByTestId("reply-input").fill("This is exactly the approach I use for my world.");
    await page.getByRole("button", { name: "Post reply" }).click();
    await expect(page.getByTestId("reply-input")).toHaveValue("");
  });

  test("care circle forum thread reply adds a post", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/community/forums/2");

    await expect(page.getByTestId("reply-composer")).toBeVisible();
    await page.getByTestId("reply-input").fill("We found a gentle stretching routine that works well.");
    await page.getByRole("button", { name: "Post reply" }).click();
    await expect(page.getByTestId("reply-input")).toHaveValue("");
  });
});

test.describe("Blog app-scoped routes", () => {
  test("storytelling app home page shows 5 recent blog posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling");

    const section = page.getByTestId("recent-blog-posts");
    await expect(section).toBeVisible();
    await expect(section.getByText("Writing Rituals That Stick")).toBeVisible();
    await expect(section.getByText("Character Voice Worksheets")).toBeVisible();
    await expect(section.getByText("Building Fantasy Economies")).toBeVisible();
    await expect(section.getByText("AI Prompting for Dialogue")).toBeVisible();
    await expect(section.getByText("Introducing World Builder 2.0")).toBeVisible();
  });

  test("care circle family home page shows recent blog posts", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family");

    const section = page.getByTestId("recent-blog-posts");
    await expect(section).toBeVisible();
    await expect(section.getByText("Care Circle Scheduling Tips")).toBeVisible();
    await expect(section.getByText("Using Memory Lane with Photos")).toBeVisible();
    await expect(section.getByText("Welcome to Care Circle")).toBeVisible();
  });

  test("storytelling blog dashboard loads and creates a post", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/storytelling/blog/new");

    await expect(page.getByRole("heading", { name: "New post" })).toBeVisible();
    await page.getByTestId("post-title-input").fill("My New Storytelling Post");
    await page.getByTestId("post-content-input").fill("This is content for my storytelling blog.");
    await page.getByRole("button", { name: "Publish" }).click();

    await expect(page).toHaveURL(/\/storytelling\/blog$/, { timeout: 15000 });
    await expect(page.getByText("My New Storytelling Post")).toBeVisible();
  });

  test("care circle blog dashboard loads and creates a post", async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });
    await page.goto("/care-circle-family/blog/new");

    await expect(page.getByRole("heading", { name: "New post" })).toBeVisible();
    await page.getByTestId("post-title-input").fill("My New Care Circle Post");
    await page.getByTestId("post-content-input").fill("This is content for my care circle blog.");
    await page.getByRole("button", { name: "Publish" }).click();

    await expect(page).toHaveURL(/\/care-circle-family\/blog$/, { timeout: 15000 });
    await expect(page.getByText("My New Care Circle Post")).toBeVisible();
  });
});
