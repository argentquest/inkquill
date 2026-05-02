import { test, expect } from "@playwright/test";
import { mockAppApis } from "./helpers";

const worldBuilderQuestionsSeed = [
  {
    id: 1,
    short_label: "Setting",
    full_question: "What kind of setting do you want?",
    answers: [
      { id: 101, text: "High fantasy" },
      { id: 102, text: "Science fiction" },
    ],
  },
  {
    id: 2,
    short_label: "Mood",
    full_question: "What mood should the world have?",
    answers: [
      { id: 201, text: "Hopeful" },
      { id: 202, text: "Grimdark" },
    ],
  },
];

const worldBuilderGeneratedSeed = {
  short_description: "A hopeful high-fantasy realm.",
  description: "A vast realm where ancient magic and modern hope intertwine beneath twin moons.",
  visual_prompt: "Twin moons over crystalline spires.",
  answer_summary: [{ question: "Setting", answer: "High fantasy" }],
};

const worldChatSessionsSeed = [
  { id: 301, world_id: 1, user_id: 7, title: "World Chat 1", created_at: "2026-04-20T10:00:00Z", updated_at: "2026-04-20T10:00:00Z" },
];

let worldChatMessagesSeed = [
  { id: 801, session_id: 301, role: "user", content: "Hello", created_at: "2026-04-20T10:01:00Z" },
  { id: 802, session_id: 301, role: "assistant", content: "Greetings!", created_at: "2026-04-20T10:01:05Z" },
];

const storyChatSessionsSeed = [
  { id: 401, story_id: 1, user_id: 7, title: "Story Chat 1", description: null, focus_area: null, created_at: "2026-04-20T10:00:00Z", updated_at: "2026-04-20T10:00:00Z" },
];

const locationHierarchySeed = [
  {
    parent: { id: null, name: "Root", scale: null },
    children: [
      { id: 201, name: "Skydock Seven", scale: "CITY" },
      { id: 202, name: "Crystal Spire", scale: "BUILDING" },
    ],
  },
];

const locationsWithCoordsSeed = [
  {
    id: 201,
    world_id: 1,
    name: "Skydock Seven",
    description: "Aerial port",
    atmosphere: "Bustling",
    significance: "Trade hub",
    scale: "CITY",
    geography: "Floating island",
    importance_rating: 4,
    map_x: 10,
    map_y: 20,
    map_z: null,
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-20T10:00:00Z",
  },
  {
    id: 202,
    world_id: 1,
    name: "Crystal Spire",
    description: "A tall tower",
    scale: "BUILDING",
    map_x: 50,
    map_y: 60,
    map_z: null,
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-20T10:00:00Z",
  },
];

test.describe("Sprint 08: Story Chat, Builder, and Spatial", () => {
  test.beforeEach(async ({ page }) => {
    worldChatMessagesSeed = [
      { id: 801, session_id: 301, role: "user", content: "Hello", created_at: "2026-04-20T10:01:00Z" },
      { id: 802, session_id: 301, role: "assistant", content: "Greetings!", created_at: "2026-04-20T10:01:05Z" },
    ];

    await mockAppApis(page, { session: "authenticated" });

    // World builder
    await page.route("**/api/v1/world-builder/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.endsWith("/world-builder/questions") && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { questions: worldBuilderQuestionsSeed } }) });
        return;
      }

      if (url.endsWith("/world-builder/generate") && method === "POST") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: worldBuilderGeneratedSeed }) });
        return;
      }

      if (url.endsWith("/world-builder/create") && method === "POST") {
        const body = route.request().postDataJSON() as { name?: string };
        await route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: {
              id: 99,
              name: body.name ?? "New World",
              short_description: worldBuilderGeneratedSeed.short_description,
              user_id: 7,
              is_free_chat_enabled: false,
              created_at: "2026-05-01T10:00:00Z",
              updated_at: "2026-05-01T10:00:00Z",
            },
          }),
        });
        return;
      }

      await route.fallback();
    });

    // World chat
    await page.route("**/api/v1/world-chat/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      const sessionsListMatch = url.match(/\/world-chat\/sessions\/(\d+)$/);
      if (sessionsListMatch && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { sessions: worldChatSessionsSeed, total: worldChatSessionsSeed.length } }) });
        return;
      }

      if (sessionsListMatch && method === "POST") {
        const newSession = {
          id: 302,
          world_id: Number(sessionsListMatch[1]),
          user_id: 7,
          title: "New session",
          created_at: "2026-05-01T10:00:00Z",
          updated_at: "2026-05-01T10:00:00Z",
        };
        await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ success: true, data: newSession }) });
        return;
      }

      const sessionDetailMatch = url.match(/\/world-chat\/sessions\/(\d+)\/(\d+)$/);
      if (sessionDetailMatch && method === "GET") {
        const sessionId = Number(sessionDetailMatch[2]);
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: {
              ...(worldChatSessionsSeed.find((s) => s.id === sessionId) ?? worldChatSessionsSeed[0]),
              messages: worldChatMessagesSeed,
            },
          }),
        });
        return;
      }

      const sendMatch = url.match(/\/world-chat\/sessions\/(\d+)\/(\d+)\/messages$/);
      if (sendMatch && method === "POST") {
        const body = route.request().postDataJSON() as { message?: string };
        const sessionId = Number(sendMatch[2]);
        const userMsg = { id: 803 + worldChatMessagesSeed.length, session_id: sessionId, role: "user", content: body.message ?? "", created_at: "2026-05-01T10:00:00Z" };
        const aiMsg = { id: 804 + worldChatMessagesSeed.length, session_id: sessionId, role: "assistant", content: "Understood.", created_at: "2026-05-01T10:00:01Z" };
        worldChatMessagesSeed = [...worldChatMessagesSeed, userMsg, aiMsg];
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: {
              user_message: userMsg,
              ai_response: aiMsg,
              session_updated_at: "2026-05-01T10:00:01Z",
            },
          }),
        });
        return;
      }

      const deleteMatch = url.match(/\/world-chat\/sessions\/(\d+)\/(\d+)$/);
      if (deleteMatch && method === "DELETE") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { message: "Deleted" } }) });
        return;
      }

      await route.fallback();
    });

    // Story chat
    await page.route("**/api/v1/story-chat/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      const sessionsListMatch = url.match(/\/story-chat\/stories\/(\d+)\/sessions$/);
      if (sessionsListMatch && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: storyChatSessionsSeed }) });
        return;
      }

      if (sessionsListMatch && method === "POST") {
        const body = route.request().postDataJSON() as { title?: string };
        const newSession = {
          id: 402,
          story_id: Number(sessionsListMatch[1]),
          user_id: 7,
          title: body.title ?? "New session",
          description: null,
          focus_area: null,
          created_at: "2026-05-01T10:00:00Z",
          updated_at: "2026-05-01T10:00:00Z",
        };
        await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ success: true, data: newSession }) });
        return;
      }

      const sessionDetailMatch = url.match(/\/story-chat\/stories\/(\d+)\/sessions\/(\d+)$/);
      if (sessionDetailMatch && method === "GET") {
        const sessionId = Number(sessionDetailMatch[2]);
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: {
              ...(storyChatSessionsSeed.find((s) => s.id === sessionId) ?? storyChatSessionsSeed[0]),
              messages: [
                { id: 901, session_id: sessionId, role: "user", content: "Hello", created_at: "2026-04-20T10:01:00Z" },
              ],
            },
          }),
        });
        return;
      }

      const deleteMatch = url.match(/\/story-chat\/stories\/(\d+)\/sessions\/(\d+)$/);
      if (deleteMatch && method === "DELETE") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { message: "Deleted" } }) });
        return;
      }

      await route.fallback();
    });

    // WS ticket
    await page.route("**/api/v1/auth/ws-ticket", async (route) => {
      if (route.request().method() === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ticket: "mock-ws-ticket" } }) });
        return;
      }
      await route.fallback();
    });

    // Location hierarchy
    await page.route("**/api/v1/worlds/**/location-connections/hierarchy", async (route) => {
      if (route.request().method() === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: locationHierarchySeed }) });
        return;
      }
      await route.fallback();
    });

    // Locations with coords (map)
    await page.route("**/api/v1/worlds/**/locations**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.match(/\/worlds\/\d+\/locations\/$/) && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: locationsWithCoordsSeed }) });
        return;
      }

      await route.fallback();
    });
  });

  test("world builder loads questions and can create world", async ({ page }) => {
    await page.goto("/storytelling/world-builder");
    await expect(page).toHaveURL(/\/storytelling\/world-builder/, { timeout: 15000 });

    await expect(page.getByText("What kind of setting do you want?")).toBeVisible();
    await page.getByText("High fantasy").click();
    await page.getByText("Hopeful").click();

    await page.getByRole("button", { name: /Generate world/i }).click();
    await expect(page.getByText("Crafting your world with AI…")).toBeVisible();

    await expect(page.getByText("A hopeful high-fantasy realm.")).toBeVisible({ timeout: 10000 });
    await page.getByLabel(/World name/i).fill("Aethoria II");
    await page.getByRole("button", { name: /Create world/i }).click();

    await expect(page.getByText("World created!")).toBeVisible({ timeout: 10000 });
  });

  test("world chat loads and can send a message", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/chat");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/chat/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Chat", exact: true })).toBeVisible();
    await expect(page.getByText("World Chat 1")).toBeVisible();

    await page.getByText("World Chat 1").click();
    await expect(page.getByText("Hello")).toBeVisible();

    await page.getByPlaceholder("Type a message...").fill("What is the weather?");
    await page.getByRole("button", { name: "Send message" }).click();
    await expect(page.getByText("What is the weather?")).toBeVisible();
  });

  test("story chat loads sessions", async ({ page }) => {
    await page.goto("/storytelling/stories/1/chat");
    await expect(page).toHaveURL(/\/storytelling\/stories\/1\/chat/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Chat", exact: true })).toBeVisible();
    await expect(page.getByText("Story Chat 1")).toBeVisible();
  });

  test("location hierarchy loads tree", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/hierarchy");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/hierarchy/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Location Hierarchy" })).toBeVisible();
    await expect(page.getByText("Skydock Seven")).toBeVisible();
    await expect(page.getByText("Crystal Spire")).toBeVisible();
  });

  test("map loads pinned locations", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/map");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/map/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Map" })).toBeVisible();
    await expect(page.getByText("Skydock Seven")).toBeVisible();
    await expect(page.getByText("Crystal Spire")).toBeVisible();
  });
});
