/**
 * Server-side helpers for the care-circle template admin API routes.
 *
 * These functions read/write provider HTML templates and theme CSS from the
 * Python backend's providers directory.  They run only inside Next.js Route
 * Handlers (edge/Node runtime); never import this in client components.
 */

import fs from "node:fs/promises";
import path from "node:path";

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------

/** Absolute path to the Python providers directory (relative to project root). */
const PROVIDERS_ROOT = path.resolve(
  process.cwd(),
  "..",
  "app",
  "services",
  "care_circle",
  "providers",
);

const THEMES_DIR = path.join(PROVIDERS_ROOT, "themes");

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ProviderInventoryEntry {
  providerKey: string;
  label: string;
  hasTemplate: boolean;
  themes: string[];
}

export interface TemplateEditorDocument {
  providerKey: string;
  theme: string;
  templateHtml: string;
  providerThemeCss: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function listDirectories(dir: string): Promise<string[]> {
  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    return entries
      .filter((e) => e.isDirectory() && !e.name.startsWith("_") && !e.name.startsWith("."))
      .map((e) => e.name);
  } catch {
    return [];
  }
}

async function readFileOrEmpty(filePath: string): Promise<string> {
  try {
    return await fs.readFile(filePath, "utf-8");
  } catch {
    return "";
  }
}

async function readConfigLabel(providerKey: string): Promise<string> {
  try {
    const configPath = path.join(PROVIDERS_ROOT, providerKey, "config.json");
    const raw = await fs.readFile(configPath, "utf-8");
    const config = JSON.parse(raw) as { name?: string };
    return config.name ?? providerKey;
  } catch {
    return providerKey;
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function readAvailableThemes(): Promise<string[]> {
  try {
    const entries = await fs.readdir(THEMES_DIR, { withFileTypes: true });
    return entries
      .filter((e) => e.isFile() && e.name.endsWith(".css"))
      .map((e) => e.name.replace(/\.css$/, ""));
  } catch {
    return ["classic"];
  }
}

export async function readTemplateInventory(): Promise<ProviderInventoryEntry[]> {
  const providerKeys = await listDirectories(PROVIDERS_ROOT);
  const themes = await readAvailableThemes();

  const entries: ProviderInventoryEntry[] = [];
  for (const key of providerKeys) {
    if (key === "memory_lane_photo" || key === "nature_scene") continue; // disabled per task

    const templateDir = path.join(PROVIDERS_ROOT, key, "templates");
    const defaultTemplate = path.join(templateDir, "default.html");
    let hasTemplate = false;
    try {
      await fs.access(defaultTemplate);
      hasTemplate = true;
    } catch {
      // no template — still include in inventory
    }

    const label = await readConfigLabel(key);
    entries.push({ providerKey: key, label, hasTemplate, themes });
  }

  return entries;
}

/**
 * Map theme names to provider CSS file names.
 * Provider theme files are conventionally named master_online.css and master_print.css.
 */
function themeToFile(theme: string): string {
  const themeMap: Record<string, string> = {
    classic: "master_online",
    high_contrast: "master_online",
    soft_pastel: "master_online",
    grid_print: "master_print",
  };
  return themeMap[theme] || theme;
}

export async function readTemplateEditorDocument(
  providerKey: string,
  theme = "classic",
): Promise<TemplateEditorDocument> {
  const templatePath = path.join(PROVIDERS_ROOT, providerKey, "templates", "default.html");
  const themeDir = path.join(PROVIDERS_ROOT, providerKey, "themes");
  const fileName = themeToFile(theme);
  const themeCssPath = path.join(themeDir, `${fileName}.css`);

  const templateHtml = await readFileOrEmpty(templatePath);
  const providerThemeCss = await readFileOrEmpty(themeCssPath);

  return { providerKey, theme, templateHtml, providerThemeCss };
}

export async function saveTemplateEditorDocument(payload: {
  providerKey: string;
  theme: string;
  templateHtml: string;
  providerThemeCss: string;
}): Promise<void> {
  const templateDir = path.join(PROVIDERS_ROOT, payload.providerKey, "templates");
  const themeDir = path.join(PROVIDERS_ROOT, payload.providerKey, "themes");
  await fs.mkdir(templateDir, { recursive: true });
  await fs.mkdir(themeDir, { recursive: true });

  await fs.writeFile(path.join(templateDir, "default.html"), payload.templateHtml, "utf-8");
  const fileName = themeToFile(payload.theme);
  await fs.writeFile(
    path.join(themeDir, `${fileName}.css`),
    payload.providerThemeCss,
    "utf-8",
  );
}
