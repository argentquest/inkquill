import { test, expect } from "@playwright/test";
import { mockAppApis } from "./helpers";

const storyDetailSeed = {
  id: 1,
  title: "The Silver Compass",
  short_description: "An explorer discovers a map that leads to an ancient realm hidden inside a storm.",
  story_genre: "Fantasy Adventure",
  story_type: "advanced",
  story_tone: "Hopeful",
  primary_conflict_type: "Character vs. Nature",
  world_id: 1,
  user_id: 7,
  ai_summary: null,
  image_url: null,
  image_prompt_definition: null,
  created_at: "2026-04-20T10:00:00Z",
  updated_at: "2026-04-25T14:30:00Z",
};

const actsSeed = [
  { id: 10, title: "The Map", description: "The explorer finds the map in a dusty attic.", act_number: 1, story_id: 1, act_summary: null, ai_summary: null, writer_notes: null, image_url: null, created_at: "2026-04-20T10:00:00Z", updated_at: "2026-04-20T10:00:00Z" },
];

test.describe("Sprint 05: Story Backbone", () => {
  test.beforeEach(async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });

    await page.route("**/api/v1/stories**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.endsWith("/stories/") && method === "POST") {
        const body = route.request().postDataJSON();
        const newStory = {
          id: 99,
          ...body,
          user_id: 7,
          world_id: body.world_id ?? 1,
          created_at: "2026-05-01T10:00:00Z",
          updated_at: "2026-05-01T10:00:00Z",
        };
        await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ success: true, data: newStory }) });
        return;
      }

      const storyMatch = url.match(/\/stories\/(\d+)$/);
      if (storyMatch) {
        const storyId = Number(storyMatch[1]);
        if (method === "GET") {
          await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...storyDetailSeed, id: storyId } }) });
          return;
        }
        if (method === "PUT") {
          const body = route.request().postDataJSON();
          await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...storyDetailSeed, id: storyId, ...body } }) });
          return;
        }
        if (method === "DELETE") {
          await route.fulfill({ status: 204, body: "" });
          return;
        }
      }

      const publishMatch = url.match(/\/stories\/(\d+)\/publish$/);
      if (publishMatch && method === "POST") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { message: "Published", published_url: "/published/test.html", filename: "test.html", status: "published" } }) });
        return;
      }

      const upgradeMatch = url.match(/\/stories\/(\d+)\/upgrade$/);
      if (upgradeMatch && method === "POST") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...storyDetailSeed, story_type: "advanced" } }) });
        return;
      }

      const actsMatch = url.match(/\/stories\/(\d+)\/acts\/$/);
      if (actsMatch && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: actsSeed }) });
        return;
      }

      await route.fallback();
    });
  });

  test("stories list loads and shows story cards", async ({ page }) => {
    await page.goto("/storytelling/stories");
    await expect(page).toHaveURL(/\/storytelling\/stories/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "The Silver Compass" })).toBeVisible();
    await expect(page.getByRole("link", { name: /Create story/i })).toBeVisible();
  });

  test("story create form submits and navigates to detail", async ({ page }) => {
    await page.goto("/storytelling/stories/new");
    await expect(page).toHaveURL(/\/storytelling\/stories\/new/, { timeout: 15000 });

    await page.getByLabel(/Title/i).fill("Dragonspire");
    await page.getByLabel(/Genre/i).fill("Fantasy");
    await page.getByLabel(/Tone/i).fill("Dark");
    await page.getByRole("button", { name: /Create story/i }).click();

    await expect(page).toHaveURL(/\/storytelling\/stories\/\d+/, { timeout: 15000 });
  });

  test("story detail loads with metadata and acts", async ({ page }) => {
    await page.goto("/storytelling/stories/1");
    await expect(page).toHaveURL(/\/storytelling\/stories\/1/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "The Silver Compass" })).toBeVisible();
    await expect(page.getByText("Acts")).toBeVisible();
    await expect(page.getByRole("heading", { name: "The Map" })).toBeVisible();
  });

  test("story edit form loads and saves", async ({ page }) => {
    await page.goto("/storytelling/stories/1/edit");
    await expect(page).toHaveURL(/\/storytelling\/stories\/1\/edit/, { timeout: 15000 });

    await page.getByLabel(/Title/i).fill("The Silver Compass — Revised");
    await page.getByRole("button", { name: /Save changes/i }).click();

    await expect(page).toHaveURL(/\/storytelling\/stories\/1/, { timeout: 15000 });
  });

  test("story wizard flows through steps and creates story", async ({ page }) => {
    await page.goto("/storytelling/stories/wizard");
    await expect(page).toHaveURL(/\/storytelling\/stories\/wizard/, { timeout: 15000 });

    await page.getByPlaceholder(/A reluctant blacksmith/i).fill("A lost clockmaker rebuilds time.");
    await page.getByRole("button", { name: /Next/i }).click();

    await page.getByLabel(/Genre/i).fill("Steampunk");
    await page.getByRole("button", { name: /Next/i }).click();

    await page.getByLabel(/Story Title/i).fill("Clockwork Tides");
    await page.getByRole("button", { name: /Create story/i }).click();

    await expect(page).toHaveURL(/\/storytelling\/stories\/\d+/, { timeout: 15000 });
  });

  test("basic story create form submits", async ({ page }) => {
    await page.goto("/storytelling/basic-stories/new");
    await expect(page).toHaveURL(/\/storytelling\/basic-stories\/new/, { timeout: 15000 });

    await page.getByLabel(/Title/i).fill("Simple Tale");
    await page.getByRole("button", { name: /Create basic story/i }).click();

    await expect(page).toHaveURL(/\/storytelling\/basic-stories\/\d+/, { timeout: 15000 });
  });
});
