import { test, expect } from "@playwright/test";
import { mockAppApis } from "./helpers";

const actSeed = {
  id: 1,
  title: "Act One: Departure",
  description: "The hero leaves home.",
  act_number: 1,
  story_id: 1,
  act_summary: "A young pilot leaves the safety of the sky harbor to chase a rumor.",
  writer_notes: "Keep the pacing tight. Introduce the compass early.",
  image_url: null,
  created_at: "2026-04-20T10:00:00Z",
  updated_at: "2026-04-20T10:00:00Z",
};

const scenesSeed = [
  {
    id: 501,
    title: "The Compass Glows",
    content: "The brass compass began to hum...",
    summary: "The compass reacts for the first time.",
    scene_number: 10,
    act_id: 1,
    mood: "Suspenseful",
    characters_present: "Elara, Jax",
    plot_points: "Compass activation",
    image_url: null,
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-20T10:00:00Z",
  },
];

const documentsSeed = [
  {
    id: 401,
    user_id: 7,
    filename: "world-notes.pdf",
    content_type: "application/pdf",
    status: "PROCESSED",
    uploaded_at: "2026-04-25T12:00:00Z",
    updated_at: "2026-04-25T12:00:00Z",
    world_id: 1,
    error_message: null,
    blob_storage_path: null,
    processed_at: "2026-04-25T12:05:00Z",
    blob_url: null,
  },
];

test.describe("Sprint 07: Editors and Documents", () => {
  let scenes: typeof scenesSeed;
  let documents: typeof documentsSeed;

  test.beforeEach(async ({ page }) => {
    scenes = [...scenesSeed];
    documents = [...documentsSeed];

    await mockAppApis(page, { session: "authenticated" });

    // Act detail, scenes list, scene create
    await page.route("**/api/v1/acts/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      const actMatch = url.match(/\/acts\/(\d+)$/);
      if (actMatch && method === "GET") {
        const actId = Number(actMatch[1]);
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...actSeed, id: actId } }) });
        return;
      }

      if (actMatch && method === "PUT") {
        const actId = Number(actMatch[1]);
        const body = route.request().postDataJSON();
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...actSeed, id: actId, ...body } }) });
        return;
      }

      const scenesMatch = url.match(/\/acts\/(\d+)\/scenes\/$/);
      if (scenesMatch && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: scenes }) });
        return;
      }

      if (scenesMatch && method === "POST") {
        const body = route.request().postDataJSON();
        const newScene = {
          id: 888 + scenes.length,
          act_id: Number(scenesMatch[1]),
          ...body,
          created_at: "2026-05-01T10:00:00Z",
          updated_at: "2026-05-01T10:00:00Z",
        };
        scenes.push(newScene);
        await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ success: true, data: newScene }) });
        return;
      }

      await route.fallback();
    });

    // Scene detail/update/delete
    await page.route("**/api/v1/scenes/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      const sceneMatch = url.match(/\/scenes\/(\d+)$/);

      if (sceneMatch && method === "GET") {
        const sceneId = Number(sceneMatch[1]);
        const scene = scenes.find((s) => s.id === sceneId) ?? scenes[0];
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...scene, id: sceneId } }) });
        return;
      }

      if (sceneMatch && method === "PUT") {
        const sceneId = Number(sceneMatch[1]);
        const body = route.request().postDataJSON();
        const idx = scenes.findIndex((s) => s.id === sceneId);
        if (idx >= 0) {
          scenes[idx] = { ...scenes[idx], ...body };
        }
        const scene = scenes.find((s) => s.id === sceneId) ?? scenes[0];
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...scene, id: sceneId } }) });
        return;
      }

      if (sceneMatch && method === "DELETE") {
        const sceneId = Number(sceneMatch[1]);
        scenes = scenes.filter((s) => s.id !== sceneId);
        await route.fulfill({ status: 204, body: "" });
        return;
      }

      await route.fallback();
    });

    // Documents list/upload/delete
    await page.route("**/api/v1/documents/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.endsWith("/documents/") && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: documents }) });
        return;
      }

      if (url.endsWith("/documents/upload") && method === "POST") {
        const newDoc = {
          id: 500 + documents.length,
          user_id: 7,
          filename: "uploaded-file.pdf",
          content_type: "application/pdf",
          status: "PENDING",
          uploaded_at: "2026-05-01T10:00:00Z",
          updated_at: "2026-05-01T10:00:00Z",
          world_id: 1,
          error_message: null,
          blob_storage_path: null,
          processed_at: null,
          blob_url: null,
        };
        documents.push(newDoc);
        await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ success: true, data: { message: "Document accepted. Processing started.", job_id: "job-888" } }) });
        return;
      }

      const docDeleteMatch = url.match(/\/documents\/(\d+)$/);
      if (docDeleteMatch && method === "DELETE") {
        const docId = Number(docDeleteMatch[1]);
        documents = documents.filter((d) => d.id !== docId);
        await route.fulfill({ status: 204, body: "" });
        return;
      }

      await route.fallback();
    });
  });

  test("act editor loads and shows scenes list", async ({ page }) => {
    await page.goto("/storytelling/acts/1");
    await expect(page).toHaveURL(/\/storytelling\/acts\/1/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: /Act One: Departure/ })).toBeVisible();
    await expect(page.getByText("The Compass Glows")).toBeVisible();
    await expect(page.getByRole("button", { name: /New scene/ })).toBeVisible();
  });

  test("act metadata can be saved", async ({ page }) => {
    await page.goto("/storytelling/acts/1");
    await expect(page).toHaveURL(/\/storytelling\/acts\/1/, { timeout: 15000 });

    await page.getByLabel(/Title/i).fill("Act One: Departure — Revised");
    await page.getByRole("button", { name: /Save act/ }).click();

    await expect(page.getByRole("heading", { name: "Act One: Departure — Revised" })).toBeVisible();
  });

  test("new scene can be created from act editor", async ({ page }) => {
    page.on("dialog", (dialog) => dialog.accept("A New Scene"));

    await page.goto("/storytelling/acts/1");
    await expect(page).toHaveURL(/\/storytelling\/acts\/1/, { timeout: 15000 });

    await page.getByRole("button", { name: /New scene/ }).click();
    await expect(page.getByText("A New Scene")).toBeVisible();
  });

  test("scene editor loads and can save changes", async ({ page }) => {
    await page.goto("/storytelling/scenes/501");
    await expect(page).toHaveURL(/\/storytelling\/scenes\/501/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "The Compass Glows" })).toBeVisible();
    await page.getByLabel(/Title/i).fill("The Compass Glows — Revised");
    await page.getByRole("button", { name: /Save scene/ }).click();

    await expect(page.getByRole("heading", { name: "The Compass Glows — Revised" })).toBeVisible();
  });

  test("scene can be deleted from scene editor", async ({ page }) => {
    page.on("dialog", (dialog) => dialog.accept());

    await page.goto("/storytelling/scenes/501");
    await expect(page).toHaveURL(/\/storytelling\/scenes\/501/, { timeout: 15000 });

    await page.getByRole("button", { name: /Delete$/ }).click();
    await expect(page).toHaveURL(/\/storytelling\/acts\/1/, { timeout: 15000 });
  });

  test("documents manager loads and shows uploads", async ({ page }) => {
    await page.goto("/storytelling/documents");
    await expect(page).toHaveURL(/\/storytelling\/documents/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Documents", exact: true })).toBeVisible();
    await expect(page.getByText("world-notes.pdf")).toBeVisible();
    await expect(page.getByText("PROCESSED")).toBeVisible();
  });

  test("document can be deleted", async ({ page }) => {
    page.on("dialog", (dialog) => dialog.accept());

    await page.goto("/storytelling/documents");
    await expect(page).toHaveURL(/\/storytelling\/documents/, { timeout: 15000 });

    await page.getByRole("button", { name: /Delete$/ }).click();
    await expect(page.getByText("world-notes.pdf")).not.toBeVisible();
  });
});
