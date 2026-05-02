import { test, expect } from "@playwright/test";
import { mockAppApis } from "./helpers";

const worldSeed = {
  id: 1,
  name: "Aethoria",
  short_description: "A realm of floating islands and ancient sky bridges connecting lost civilisations.",
  description: "A realm of floating islands and ancient sky bridges connecting lost civilisations.",
  is_free_chat_enabled: false,
  user_id: 7,
  created_at: "2026-04-18T09:00:00Z",
  updated_at: "2026-04-24T11:00:00Z",
};

const charactersSeed = [
  {
    id: 101,
    world_id: 1,
    name: "Elara Vance",
    gender: "Female",
    species: "Human",
    description: "A sky-pirate captain with a mechanical arm and a grudge against the empire.",
    personality_traits: "Bold, cunning, loyal",
    backstory: "Born on the lowest floating island, she clawed her way up through the merchant fleets.",
    importance_rating: 5,
    relationships: "Rival of Captain Korr, mentor to Jax",
    profession: "Sky Pirate Captain",
    age_category: "Young Adult",
    image_url: null,
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-20T10:00:00Z",
  },
];

const locationsSeed = [
  {
    id: 201,
    world_id: 1,
    name: "Skydock Seven",
    description: "The largest aerial port in the western archipelago.",
    atmosphere: "Bustling, chaotic, fragrant with engine oil",
    significance: "Major trade hub and smuggling entry point.",
    scale: "CITY",
    geography: "Built onto the underbelly of a massive floating island.",
    importance_rating: 4,
    image_url: null,
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-20T10:00:00Z",
  },
];

const loreItemsSeed = [
  {
    id: 301,
    world_id: 1,
    title: "The Skyforged Treaty",
    description: "An ancient pact that keeps the floating islands aloft.",
    category: "HISTORICAL_EVENT",
    importance_rating: 5,
    related_elements: "Linked to Skydock Seven and Elara Vance's backstory.",
    image_url: null,
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-20T10:00:00Z",
  },
];

test.describe("Sprint 06: World Elements", () => {
  test.beforeEach(async ({ page }) => {
    await mockAppApis(page, { session: "authenticated" });

    // Characters
    await page.route("**/api/v1/worlds/**/characters**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.match(/\/worlds\/\d+\/characters\/$/) && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: charactersSeed }) });
        return;
      }

      if (url.match(/\/worlds\/\d+\/characters\/$/) && method === "POST") {
        const body = route.request().postDataJSON();
        const newChar = {
          id: 999,
          world_id: 1,
          ...body,
          created_at: "2026-05-01T10:00:00Z",
          updated_at: "2026-05-01T10:00:00Z",
        };
        await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ success: true, data: newChar }) });
        return;
      }

      await route.fallback();
    });

    await page.route("**/api/v1/characters/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      const match = url.match(/\/characters\/(\d+)$/);

      if (match) {
        const charId = Number(match[1]);
        const char = charactersSeed.find((c) => c.id === charId) ?? charactersSeed[0];
        if (method === "GET") {
          await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...char, id: charId } }) });
          return;
        }
        if (method === "PUT") {
          const body = route.request().postDataJSON();
          await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...char, ...body } }) });
          return;
        }
        if (method === "DELETE") {
          await route.fulfill({ status: 204, body: "" });
          return;
        }
      }

      await route.fallback();
    });

    // Locations
    await page.route("**/api/v1/worlds/**/locations**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.match(/\/worlds\/\d+\/locations\/$/) && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: locationsSeed }) });
        return;
      }

      if (url.match(/\/worlds\/\d+\/locations\/$/) && method === "POST") {
        const body = route.request().postDataJSON();
        const newLoc = {
          id: 888,
          world_id: 1,
          ...body,
          created_at: "2026-05-01T10:00:00Z",
          updated_at: "2026-05-01T10:00:00Z",
        };
        await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ success: true, data: newLoc }) });
        return;
      }

      await route.fallback();
    });

    await page.route("**/api/v1/locations/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      const match = url.match(/\/locations\/(\d+)$/);

      if (match) {
        const locId = Number(match[1]);
        const loc = locationsSeed.find((l) => l.id === locId) ?? locationsSeed[0];
        if (method === "GET") {
          await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...loc, id: locId } }) });
          return;
        }
        if (method === "PUT") {
          const body = route.request().postDataJSON();
          await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...loc, ...body } }) });
          return;
        }
        if (method === "DELETE") {
          await route.fulfill({ status: 204, body: "" });
          return;
        }
      }

      await route.fallback();
    });

    // Lore items
    await page.route("**/api/v1/worlds/**/lore-items**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.match(/\/worlds\/\d+\/lore-items\/$/) && method === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: loreItemsSeed }) });
        return;
      }

      if (url.match(/\/worlds\/\d+\/lore-items\/$/) && method === "POST") {
        const body = route.request().postDataJSON();
        const newItem = {
          id: 777,
          world_id: 1,
          ...body,
          created_at: "2026-05-01T10:00:00Z",
          updated_at: "2026-05-01T10:00:00Z",
        };
        await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ success: true, data: newItem }) });
        return;
      }

      await route.fallback();
    });

    await page.route("**/api/v1/lore-items/**", async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      const match = url.match(/\/lore-items\/(\d+)$/);

      if (match) {
        const itemId = Number(match[1]);
        const item = loreItemsSeed.find((i) => i.id === itemId) ?? loreItemsSeed[0];
        if (method === "GET") {
          await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...item, id: itemId } }) });
          return;
        }
        if (method === "PUT") {
          const body = route.request().postDataJSON();
          await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: { ...item, ...body } }) });
          return;
        }
        if (method === "DELETE") {
          await route.fulfill({ status: 204, body: "" });
          return;
        }
      }

      await route.fallback();
    });
  });

  test("world detail loads and shows element navigation", async ({ page }) => {
    await page.goto("/storytelling/worlds/1");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Aethoria" })).toBeVisible();
    await expect(page.getByRole("link", { name: /Characters \d+/ })).toBeVisible();
    await expect(page.getByRole("link", { name: /Locations \d+/ })).toBeVisible();
    await expect(page.getByRole("link", { name: /Lore Items \d+/ })).toBeVisible();
  });

  test("characters list loads and shows character cards", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/characters");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/characters/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Characters" })).toBeVisible();
    await expect(page.getByText("Elara Vance")).toBeVisible();
    await expect(page.getByRole("link", { name: /New character/i })).toBeVisible();
  });

  test("character create form submits and navigates to detail", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/characters/new");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/characters\/new/, { timeout: 15000 });

    await page.getByLabel(/Name/i).fill("Kaelen Moonweave");
    await page.getByLabel(/Species/i).fill("Elf");
    await page.getByRole("button", { name: /Create character/i }).click();

    await expect(page).toHaveURL(/\/storytelling\/characters\/\d+/, { timeout: 15000 });
  });

  test("character detail loads and can be edited", async ({ page }) => {
    await page.goto("/storytelling/characters/101");
    await expect(page).toHaveURL(/\/storytelling\/characters\/101/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Elara Vance" })).toBeVisible();
    await page.getByLabel(/Name/i).fill("Elara Vance — Updated");
    await page.getByRole("button", { name: /Save changes/i }).click();

    await expect(page.getByRole("heading", { name: "Elara Vance — Updated" })).toBeVisible();
  });

  test("locations list loads and shows location cards", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/locations");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/locations/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Locations" })).toBeVisible();
    await expect(page.getByText("Skydock Seven")).toBeVisible();
    await expect(page.getByRole("link", { name: /New location/i })).toBeVisible();
  });

  test("location create form submits and navigates to detail", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/locations/new");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/locations\/new/, { timeout: 15000 });

    await page.getByLabel(/Name/i).fill("Crystal Spire");
    await page.getByRole("button", { name: /Create location/i }).click();

    await expect(page).toHaveURL(/\/storytelling\/locations\/\d+/, { timeout: 15000 });
  });

  test("lore items list loads and shows lore cards", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/lore-items");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/lore-items/, { timeout: 15000 });

    await expect(page.getByRole("heading", { name: "Lore Items" })).toBeVisible();
    await expect(page.getByText("The Skyforged Treaty")).toBeVisible();
    await expect(page.getByRole("link", { name: /New lore item/i })).toBeVisible();
  });

  test("lore item create form submits and navigates to detail", async ({ page }) => {
    await page.goto("/storytelling/worlds/1/lore-items/new");
    await expect(page).toHaveURL(/\/storytelling\/worlds\/1\/lore-items\/new/, { timeout: 15000 });

    await page.getByLabel(/Title/i).fill("The Ember Crown");
    await page.getByLabel(/Category/i).selectOption("ARTIFACT");
    await page.getByRole("button", { name: /Create lore item/i }).click();

    await expect(page).toHaveURL(/\/storytelling\/lore-items\/\d+/, { timeout: 15000 });
  });
});
