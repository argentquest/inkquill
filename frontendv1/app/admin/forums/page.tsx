"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Loader2,
  MessageSquare,
  Pencil,
  Plus,
  Trash2,
  XCircle,
} from "lucide-react";
import { useLayoutEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { LoadingState } from "@/components/ui/loading-state";
import {
  createForumCategory,
  deleteForumCategory,
  fetchForumCategoriesAdmin,
  updateForumCategory,
  type ForumCategory,
} from "@/lib/api";

const APP_SOURCES = [
  { value: "storytelling", label: "Storytelling" },
  { value: "care-circle", label: "Care Circle" },
] as const;

type AppSource = (typeof APP_SOURCES)[number]["value"];

// ---------------------------------------------------------------------------
// Add Category Form
// ---------------------------------------------------------------------------

interface AddCategoryFormProps {
  appSource: AppSource;
  onDone: () => void;
}

function AddCategoryForm({ appSource, onDone }: AddCategoryFormProps) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [icon, setIcon] = useState("");
  const [sortOrder, setSortOrder] = useState(0);

  const { mutate, isPending, error } = useMutation({
    mutationFn: () =>
      createForumCategory({
        name,
        description: description || undefined,
        icon: icon || undefined,
        sort_order: sortOrder,
        app_source: appSource,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-forum-categories", appSource] });
      onDone();
    },
  });

  return (
    <form
      className="space-y-4"
      data-testid="add-category-form"
      onSubmit={(e) => {
        e.preventDefault();
        mutate();
      }}
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1">
          <label className="text-xs font-medium text-ink-700" htmlFor="cat-name">
            Name <span className="text-red-500">*</span>
          </label>
          <input
            className="w-full rounded-[12px] border border-black/10 bg-white px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-ink-900/10"
            id="cat-name"
            maxLength={100}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. General Discussion"
            required
            type="text"
            value={name}
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium text-ink-700" htmlFor="cat-icon">
            Icon <span className="text-ink-400 font-normal">(emoji or short string)</span>
          </label>
          <input
            className="w-full rounded-[12px] border border-black/10 bg-white px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-ink-900/10"
            id="cat-icon"
            maxLength={50}
            onChange={(e) => setIcon(e.target.value)}
            placeholder="💬"
            type="text"
            value={icon}
          />
        </div>
      </div>
      <div className="space-y-1">
        <label className="text-xs font-medium text-ink-700" htmlFor="cat-description">
          Description
        </label>
        <textarea
          className="w-full rounded-[12px] border border-black/10 bg-white px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:outline-none focus:ring-2 focus:ring-ink-900/10"
          id="cat-description"
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional description shown to users…"
          rows={2}
          value={description}
        />
      </div>
      <div className="space-y-1 w-32">
        <label className="text-xs font-medium text-ink-700" htmlFor="cat-sort">
          Sort Order
        </label>
        <input
          className="w-full rounded-[12px] border border-black/10 bg-white px-3 py-2 text-sm text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900/10"
          id="cat-sort"
          min={0}
          onChange={(e) => setSortOrder(Number(e.target.value))}
          type="number"
          value={sortOrder}
        />
      </div>
      {error ? (
        <p className="text-xs text-red-600" data-testid="add-category-error">
          {error.message}
        </p>
      ) : null}
      <div className="flex items-center gap-2">
        <button
          className="rounded-[14px] bg-ink-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-ink-800 disabled:opacity-40"
          disabled={isPending || !name.trim()}
          type="submit"
        >
          {isPending ? <Loader2 className="size-4 animate-spin" /> : "Add Category"}
        </button>
        <button
          className="rounded-[14px] border border-black/10 px-4 py-2 text-sm font-medium text-ink-700 transition hover:bg-ink-50"
          onClick={onDone}
          type="button"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

// ---------------------------------------------------------------------------
// Edit Category Form
// ---------------------------------------------------------------------------

interface EditCategoryFormProps {
  category: ForumCategory;
  onDone: () => void;
}

function EditCategoryForm({ category, onDone }: EditCategoryFormProps) {
  const queryClient = useQueryClient();
  const [name, setName] = useState(category.name);
  const [description, setDescription] = useState(category.description ?? "");
  const [icon, setIcon] = useState(category.icon ?? "");
  const [sortOrder, setSortOrder] = useState(category.sort_order);

  const { mutate, isPending, error } = useMutation({
    mutationFn: () =>
      updateForumCategory(category.id, {
        name,
        description: description || null,
        icon: icon || null,
        sort_order: sortOrder,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["admin-forum-categories", category.app_source],
      });
      onDone();
    },
  });

  return (
    <form
      className="mt-3 space-y-3 border-t border-black/6 pt-3"
      data-testid="edit-category-form"
      onSubmit={(e) => {
        e.preventDefault();
        mutate();
      }}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1">
          <label className="text-xs font-medium text-ink-700">Name</label>
          <input
            className="w-full rounded-[10px] border border-black/10 bg-white px-3 py-1.5 text-sm text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900/10"
            maxLength={100}
            onChange={(e) => setName(e.target.value)}
            required
            type="text"
            value={name}
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium text-ink-700">Icon</label>
          <input
            className="w-full rounded-[10px] border border-black/10 bg-white px-3 py-1.5 text-sm text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900/10"
            maxLength={50}
            onChange={(e) => setIcon(e.target.value)}
            placeholder="💬"
            type="text"
            value={icon}
          />
        </div>
      </div>
      <div className="space-y-1">
        <label className="text-xs font-medium text-ink-700">Description</label>
        <textarea
          className="w-full rounded-[10px] border border-black/10 bg-white px-3 py-1.5 text-sm text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900/10"
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          value={description}
        />
      </div>
      <div className="space-y-1 w-28">
        <label className="text-xs font-medium text-ink-700">Sort Order</label>
        <input
          className="w-full rounded-[10px] border border-black/10 bg-white px-3 py-1.5 text-sm text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900/10"
          min={0}
          onChange={(e) => setSortOrder(Number(e.target.value))}
          type="number"
          value={sortOrder}
        />
      </div>
      {error ? (
        <p className="text-xs text-red-600">{error.message}</p>
      ) : null}
      <div className="flex items-center gap-2">
        <button
          className="rounded-[12px] bg-ink-900 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-ink-800 disabled:opacity-40"
          disabled={isPending || !name.trim()}
          type="submit"
        >
          {isPending ? <Loader2 className="size-3 animate-spin" /> : "Save Changes"}
        </button>
        <button
          className="rounded-[12px] border border-black/10 px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:bg-ink-50"
          onClick={onDone}
          type="button"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

// ---------------------------------------------------------------------------
// Category Row
// ---------------------------------------------------------------------------

interface CategoryRowProps {
  appSource: AppSource;
  category: ForumCategory;
}

function CategoryRow({ appSource, category }: CategoryRowProps) {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);

  const { mutate: toggle, isPending: toggling } = useMutation({
    mutationFn: () => updateForumCategory(category.id, { is_active: !category.is_active }),
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ["admin-forum-categories", appSource] }),
  });

  const { mutate: remove, isPending: removing } = useMutation({
    mutationFn: () => deleteForumCategory(category.id),
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ["admin-forum-categories", appSource] }),
  });

  return (
    <div
      className="rounded-[20px] border border-black/8 bg-white px-5 py-4"
      data-testid="category-row"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            {category.icon ? (
              <span className="text-base leading-none">{category.icon}</span>
            ) : null}
            <p className="font-medium text-ink-900 text-sm">{category.name}</p>
            <span className="rounded-full bg-ink-900/6 px-2 py-0.5 text-xs text-ink-500 font-mono">
              {category.slug}
            </span>
            <span className="rounded-full bg-ink-900/6 px-2 py-0.5 text-xs text-ink-500">
              {category.thread_count} thread{category.thread_count !== 1 ? "s" : ""}
            </span>
            <span className="rounded-full bg-ink-900/6 px-2 py-0.5 text-xs text-ink-500">
              order: {category.sort_order}
            </span>
            <span
              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                category.is_active
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-red-50 text-red-600"
              }`}
              data-testid="category-status-badge"
            >
              {category.is_active ? (
                <>
                  <CheckCircle2 className="size-3" /> Active
                </>
              ) : (
                <>
                  <XCircle className="size-3" /> Inactive
                </>
              )}
            </span>
          </div>
          {category.description ? (
            <p className="mt-1 text-xs text-ink-500 truncate">{category.description}</p>
          ) : null}
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <button
            className="rounded-[14px] border border-black/10 bg-white px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:border-black/20 hover:bg-ink-50 disabled:opacity-40"
            data-testid="edit-category-button"
            onClick={() => setEditing((v) => !v)}
            type="button"
          >
            <Pencil className="size-3" />
          </button>
          <button
            className="rounded-[14px] border border-black/10 bg-white px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:border-black/20 hover:bg-ink-50 disabled:opacity-40"
            data-testid="toggle-category-button"
            disabled={toggling}
            onClick={() => toggle()}
            type="button"
          >
            {toggling ? (
              <Loader2 className="size-3 animate-spin" />
            ) : category.is_active ? (
              "Disable"
            ) : (
              "Enable"
            )}
          </button>
          <button
            className="rounded-[14px] border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-100 disabled:opacity-40"
            data-testid="delete-category-button"
            disabled={removing}
            onClick={() => {
              if (
                window.confirm(
                  `Delete category "${category.name}"? This cannot be undone and will fail if threads exist.`
                )
              ) {
                remove();
              }
            }}
            type="button"
          >
            {removing ? <Loader2 className="size-3 animate-spin" /> : <Trash2 className="size-3" />}
          </button>
        </div>
      </div>

      {editing ? (
        <EditCategoryForm category={category} onDone={() => setEditing(false)} />
      ) : null}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function AdminForumsPage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;
  const searchParams = useSearchParams();
  const initialApp = searchParams.get("app_source") === "care-circle" ? "care-circle" : "storytelling";
  const [appSource, setAppSource] = useState<AppSource>(initialApp);
  const [showAddForm, setShowAddForm] = useState(false);

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace("/auth/login?next=/admin/forums");
    } else if (session.status === "authenticated" && !isAdmin) {
      window.location.replace("/access-denied?surface=admin");
    }
  }, [session.status, isAdmin]);

  const { data: categories = [], isLoading, isError } = useQuery({
    queryKey: ["admin-forum-categories", appSource],
    queryFn: () => fetchForumCategoriesAdmin({ app_source: appSource, include_inactive: true }),
    enabled: isAdmin,
  });

  if (session.status === "loading" || (session.status === "authenticated" && !isAdmin)) {
    return <LoadingState label="Checking access" />;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Admin › Forums"
        title="Forum Categories"
        description="Manage categories for each app. Add, edit, enable, or disable categories."
      />

      {/* App selector */}
      <div className="flex items-center gap-2">
        {APP_SOURCES.map(({ value, label }) => (
          <button
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
              appSource === value
                ? "bg-ink-900 text-white"
                : "border border-black/10 bg-white text-ink-700 hover:bg-ink-50"
            }`}
            data-testid={`app-source-tab-${value}`}
            key={value}
            onClick={() => {
              setAppSource(value);
              setShowAddForm(false);
            }}
            type="button"
          >
            {label}
          </button>
        ))}
      </div>

      {/* Category list */}
      <div className="rounded-[24px] border border-black/10 bg-white/70 p-6 shadow-panel space-y-4">
        {isLoading ? (
          <div className="flex items-center gap-2 text-sm text-ink-500">
            <Loader2 className="size-4 animate-spin" /> Loading categories…
          </div>
        ) : isError ? (
          <p className="text-sm text-red-600" data-testid="categories-error">
            Failed to load categories.
          </p>
        ) : categories.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-8 text-ink-400" data-testid="categories-empty">
            <MessageSquare className="size-8 opacity-40" />
            <p className="text-sm">No categories yet for {appSource}.</p>
          </div>
        ) : (
          <div className="space-y-3" data-testid="category-list">
            {categories.map((cat) => (
              <CategoryRow appSource={appSource} category={cat} key={cat.id} />
            ))}
          </div>
        )}

        {/* Add new */}
        <div className="border-t border-black/6 pt-4">
          <button
            className="flex items-center gap-1.5 text-sm font-medium text-ink-700 hover:text-ink-900 transition"
            data-testid="toggle-add-category"
            onClick={() => setShowAddForm((v) => !v)}
            type="button"
          >
            {showAddForm ? (
              <>
                <ChevronUp className="size-4" /> Hide form
              </>
            ) : (
              <>
                <Plus className="size-4" /> Add Category
              </>
            )}
          </button>
          {showAddForm ? (
            <div className="mt-4">
              <AddCategoryForm
                appSource={appSource}
                onDone={() => setShowAddForm(false)}
              />
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
