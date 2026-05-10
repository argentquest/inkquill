"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Pencil, Plus, Trash2, X } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import {
  adminFetchTagTaxonomy,
  adminCreateTagTaxonomyEntry,
  adminUpdateTagTaxonomyEntry,
  adminDeleteTagTaxonomyEntry,
  adminRenameTagTaxonomyCategory,
  type TagTaxonomyEntry,
} from "@/lib/api";

const FIELD_KEYS = [
  { key: "hobbies", label: "Hobbies" },
  { key: "favoriteActivities", label: "Activities" },
  { key: "lifeRoles", label: "Life Roles" },
  { key: "pets", label: "Pets" },
  { key: "favouriteFoods", label: "Foods" },
  { key: "favouriteTvShows", label: "TV Shows" },
  { key: "favoriteSingers", label: "Singers" },
];

const SOURCE_COLORS: Record<string, string> = {
  curated: "bg-forest/10 text-forest",
  onet: "bg-sky-100 text-sky-800",
  musicbrainz: "bg-violet-100 text-violet-800",
  wikidata: "bg-amber-100 text-amber-800",
};

function SourceBadge({ source }: { source: string }) {
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SOURCE_COLORS[source] ?? "bg-ink-100 text-ink-700"}`}>
      {source}
    </span>
  );
}

function InlineEdit({
  value,
  onSave,
  onCancel,
}: {
  value: string;
  onSave: (v: string) => void;
  onCancel: () => void;
}) {
  const [text, setText] = useState(value);
  return (
    <span className="inline-flex items-center gap-1">
      <input
        autoFocus
        className="rounded-lg border border-black/20 bg-white px-2 py-0.5 text-sm text-ink-900 outline-none"
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") onSave(text.trim());
          if (e.key === "Escape") onCancel();
        }}
        value={text}
      />
      <button className="text-forest hover:opacity-70" onClick={() => onSave(text.trim())} type="button">
        <Check className="h-3.5 w-3.5" />
      </button>
      <button className="text-ember hover:opacity-70" onClick={onCancel} type="button">
        <X className="h-3.5 w-3.5" />
      </button>
    </span>
  );
}

export default function TagTaxonomyPage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;
  const queryClient = useQueryClient();

  const [activeFieldKey, setActiveFieldKey] = useState(FIELD_KEYS[0].key);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingCategory, setEditingCategory] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCategory, setNewCategory] = useState("");
  const [newLabel, setNewLabel] = useState("");

  const { data: entries, isLoading, isError } = useQuery({
    queryKey: ["admin-tag-taxonomy"],
    queryFn: adminFetchTagTaxonomy,
    enabled: isAdmin,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["admin-tag-taxonomy"] });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof adminUpdateTagTaxonomyEntry>[1] }) =>
      adminUpdateTagTaxonomyEntry(id, data),
    onSuccess: () => { invalidate(); setEditingId(null); },
  });

  const deleteMutation = useMutation({
    mutationFn: adminDeleteTagTaxonomyEntry,
    onSuccess: () => { invalidate(); setDeleteConfirmId(null); },
  });

  const createMutation = useMutation({
    mutationFn: adminCreateTagTaxonomyEntry,
    onSuccess: () => { invalidate(); setNewCategory(""); setNewLabel(""); setShowAddForm(false); },
  });

  const renameMutation = useMutation({
    mutationFn: ({ fieldKey, oldCat, newCat }: { fieldKey: string; oldCat: string; newCat: string }) =>
      adminRenameTagTaxonomyCategory(fieldKey, oldCat, newCat),
    onSuccess: () => { invalidate(); setEditingCategory(null); },
  });

  if (!isAdmin) {
    return <ErrorState title="Access denied" detail="Admin access required." />;
  }

  if (isLoading) return <LoadingState label="Loading taxonomy…" />;
  if (isError || !entries) return <ErrorState title="Could not load taxonomy" detail="Try refreshing the page." />;

  const fieldEntries = entries.filter((e) => e.fieldKey === activeFieldKey);
  const categories = [...new Set(fieldEntries.map((e) => e.category))].sort();

  // Collect all categories across all entries for the new-entry dropdown
  const allCategoriesForField = [...new Set(fieldEntries.map((e) => e.category))].sort();

  return (
    <div className="space-y-8">
      <PageHeader
        description="Browse, enable/disable, add, edit, and rename taxonomy entries used in friend profile suggestions."
        eyebrow="Admin"
        title="Tag Taxonomy"
      />

      {/* Field selector tabs */}
      <nav className="flex flex-wrap gap-1 rounded-2xl border border-black/10 bg-white/70 p-1.5 shadow-sm">
        {FIELD_KEYS.map((f) => (
          <button
            key={f.key}
            className={[
              "rounded-xl px-4 py-2 text-sm font-medium transition",
              activeFieldKey === f.key
                ? "bg-ink-900 text-white shadow-sm"
                : "text-ink-700 hover:bg-black/[0.05] hover:text-ink-900",
            ].join(" ")}
            onClick={() => { setActiveFieldKey(f.key); setShowAddForm(false); }}
            type="button"
          >
            {f.label}
            <span className="ml-1.5 text-xs opacity-60">
              {entries.filter((e) => e.fieldKey === f.key && e.isActive).length}
            </span>
          </button>
        ))}
      </nav>

      {/* Add entry form */}
      <div>
        {showAddForm ? (
          <div className="rounded-[24px] border border-black/10 bg-white/80 p-5 shadow-panel">
            <h3 className="text-sm font-bold text-ink-900">Add new entry</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div>
                <label className="block text-xs uppercase tracking-[0.2em] text-ink-600">Category</label>
                <input
                  className="mt-1 w-full rounded-xl border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-900 outline-none focus:border-black/30"
                  list="category-datalist"
                  onChange={(e) => setNewCategory(e.target.value)}
                  placeholder="e.g. Arts & Crafts"
                  value={newCategory}
                />
                <datalist id="category-datalist">
                  {allCategoriesForField.map((c) => <option key={c} value={c} />)}
                </datalist>
              </div>
              <div>
                <label className="block text-xs uppercase tracking-[0.2em] text-ink-600">Label</label>
                <input
                  className="mt-1 w-full rounded-xl border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-900 outline-none focus:border-black/30"
                  onChange={(e) => setNewLabel(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && newCategory && newLabel) {
                      createMutation.mutate({ fieldKey: activeFieldKey, category: newCategory, label: newLabel });
                    }
                  }}
                  placeholder="e.g. Watercolour painting"
                  value={newLabel}
                />
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <button
                className="rounded-full bg-ink-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-ink-700 disabled:opacity-50"
                disabled={!newCategory.trim() || !newLabel.trim() || createMutation.isPending}
                onClick={() => createMutation.mutate({ fieldKey: activeFieldKey, category: newCategory.trim(), label: newLabel.trim() })}
                type="button"
              >
                {createMutation.isPending ? "Saving…" : "Add entry"}
              </button>
              <button
                className="rounded-full border border-black/10 px-4 py-2 text-sm font-semibold text-ink-700 transition hover:bg-black/5"
                onClick={() => setShowAddForm(false)}
                type="button"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
            onClick={() => setShowAddForm(true)}
            type="button"
          >
            <Plus className="h-4 w-4" />
            Add entry
          </button>
        )}
      </div>

      {/* Entries grouped by category */}
      <div className="space-y-6">
        {categories.map((category) => {
          const catEntries = fieldEntries.filter((e) => e.category === category);
          return (
            <section key={category} className="rounded-[28px] border border-black/10 bg-white/70 shadow-panel">
              {/* Category header */}
              <div className="flex items-center justify-between border-b border-black/8 px-6 py-4">
                {editingCategory === category ? (
                  <InlineEdit
                    value={category}
                    onSave={(newCat) => {
                      if (newCat && newCat !== category) {
                        renameMutation.mutate({ fieldKey: activeFieldKey, oldCat: category, newCat });
                      } else {
                        setEditingCategory(null);
                      }
                    }}
                    onCancel={() => setEditingCategory(null)}
                  />
                ) : (
                  <span className="font-semibold text-ink-900">{category}</span>
                )}
                <div className="flex items-center gap-2">
                  <span className="text-xs text-ink-500">{catEntries.length} entries</span>
                  <button
                    className="rounded-full p-1.5 text-ink-500 transition hover:bg-black/5 hover:text-ink-900"
                    onClick={() => setEditingCategory(editingCategory === category ? null : category)}
                    title="Rename category"
                    type="button"
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

              {/* Entry rows */}
              <ul className="divide-y divide-black/5 px-6">
                {catEntries.map((entry) => (
                  <li
                    key={entry.id}
                    className={`flex items-center justify-between gap-3 py-3 ${entry.isActive ? "" : "opacity-50"}`}
                  >
                    <div className="flex min-w-0 flex-1 items-center gap-3">
                      {editingId === entry.id ? (
                        <InlineEdit
                          value={entry.label}
                          onSave={(label) => {
                            if (label) updateMutation.mutate({ id: entry.id, data: { label } });
                            else setEditingId(null);
                          }}
                          onCancel={() => setEditingId(null)}
                        />
                      ) : (
                        <span className="text-sm text-ink-900">{entry.label}</span>
                      )}
                      <SourceBadge source={entry.source} />
                    </div>

                    <div className="flex shrink-0 items-center gap-1.5">
                      {/* Toggle active */}
                      <button
                        className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                          entry.isActive
                            ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-200"
                            : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                        }`}
                        disabled={updateMutation.isPending}
                        onClick={() => updateMutation.mutate({ id: entry.id, data: { isActive: !entry.isActive } })}
                        title={entry.isActive ? "Disable" : "Enable"}
                        type="button"
                      >
                        {entry.isActive ? "Active" : "Disabled"}
                      </button>

                      {/* Edit label */}
                      <button
                        className="rounded-full p-1.5 text-ink-500 transition hover:bg-black/5 hover:text-ink-900"
                        onClick={() => setEditingId(editingId === entry.id ? null : entry.id)}
                        title="Edit label"
                        type="button"
                      >
                        <Pencil className="h-3.5 w-3.5" />
                      </button>

                      {/* Delete */}
                      {deleteConfirmId === entry.id ? (
                        <span className="inline-flex items-center gap-1 text-xs text-ember">
                          Delete?
                          <button
                            className="rounded-full bg-ember px-2 py-0.5 text-white hover:bg-ember/80"
                            disabled={deleteMutation.isPending}
                            onClick={() => deleteMutation.mutate(entry.id)}
                            type="button"
                          >
                            Yes
                          </button>
                          <button
                            className="rounded-full border border-black/10 px-2 py-0.5 hover:bg-black/5"
                            onClick={() => setDeleteConfirmId(null)}
                            type="button"
                          >
                            No
                          </button>
                        </span>
                      ) : (
                        <button
                          className="rounded-full p-1.5 text-ink-400 transition hover:bg-red-50 hover:text-ember"
                          onClick={() => setDeleteConfirmId(entry.id)}
                          title="Delete entry"
                          type="button"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          );
        })}

        {categories.length === 0 && (
          <div className="rounded-[28px] border border-black/10 bg-white/70 p-8 text-center text-sm text-ink-500">
            No entries for this field yet. Run the seed script or add entries above.
          </div>
        )}
      </div>
    </div>
  );
}
