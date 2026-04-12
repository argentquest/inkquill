"use client";

import {
  DndContext,
  DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { GripVertical, ChevronUp, ChevronDown, ToggleLeft, ToggleRight } from "lucide-react";
import { useEffect, useState } from "react";

import {
  reorderCareCirclePatientProviderConfigs,
  updateCareCirclePatientProviderConfig,
  type CareCircleProvider,
  type CareCircleProviderConfig,
} from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface ProviderRow {
  providerKey: string;
  label: string;
  icon: string;
  category: string;
  isEnabled: boolean;
  displayOrder: number;
}

interface Props {
  patientId: string;
  providerCatalog: CareCircleProvider[];
  providerConfigs: CareCircleProviderConfig[];
}

// ── Sortable row ──────────────────────────────────────────────────────────────

function SortableProviderRow({
  row,
  index,
  total,
  isPending,
  onToggle,
  onMoveUp,
  onMoveDown,
}: {
  row: ProviderRow;
  index: number;
  total: number;
  isPending: boolean;
  onToggle: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: row.providerKey });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 10 : undefined,
    opacity: isDragging ? 0.85 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-3 rounded-2xl border bg-white px-4 py-3 shadow-sm transition ${
        isDragging ? "border-ink-300 shadow-md" : "border-black/10"
      }`}
    >
      {/* Drag handle */}
      <button
        {...attributes}
        {...listeners}
        aria-label="Drag to reorder"
        className="cursor-grab touch-none text-ink-400 hover:text-ink-700 active:cursor-grabbing"
        type="button"
      >
        <GripVertical size={18} />
      </button>

      {/* Order badge */}
      <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-ink-100 text-xs font-bold text-ink-600">
        {index + 1}
      </span>

      {/* Icon + name */}
      <span className="text-xl leading-none">{row.icon || "📰"}</span>
      <div className="flex-1 min-w-0">
        <p className="truncate text-sm font-semibold text-ink-900">{row.label}</p>
        <p className="text-xs uppercase tracking-[0.2em] text-ink-500">{row.category}</p>
      </div>

      {/* Up / Down buttons */}
      <div className="flex flex-col gap-0.5">
        <button
          aria-label="Move up"
          className="rounded p-0.5 text-ink-400 hover:text-ink-800 disabled:opacity-30"
          disabled={index === 0 || isPending}
          onClick={onMoveUp}
          type="button"
        >
          <ChevronUp size={16} />
        </button>
        <button
          aria-label="Move down"
          className="rounded p-0.5 text-ink-400 hover:text-ink-800 disabled:opacity-30"
          disabled={index === total - 1 || isPending}
          onClick={onMoveDown}
          type="button"
        >
          <ChevronDown size={16} />
        </button>
      </div>

      {/* Toggle */}
      <button
        aria-label={row.isEnabled ? "Disable provider" : "Enable provider"}
        className={`flex-shrink-0 transition ${
          row.isEnabled ? "text-emerald-600 hover:text-emerald-800" : "text-slate-400 hover:text-slate-600"
        } disabled:cursor-not-allowed disabled:opacity-50`}
        disabled={isPending}
        onClick={onToggle}
        type="button"
      >
        {row.isEnabled ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
      </button>
    </div>
  );
}

// ── Disabled row (simple, no drag) ────────────────────────────────────────────

function DisabledProviderRow({
  row,
  isPending,
  onToggle,
}: {
  row: ProviderRow;
  isPending: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-black/5 bg-[#f8f9fb] px-4 py-3 opacity-60">
      <span className="w-6 flex-shrink-0" />
      <span className="text-xl leading-none">{row.icon || "📰"}</span>
      <div className="flex-1 min-w-0">
        <p className="truncate text-sm font-semibold text-ink-700">{row.label}</p>
        <p className="text-xs uppercase tracking-[0.2em] text-ink-400">{row.category}</p>
      </div>
      <button
        aria-label="Enable provider"
        className="flex-shrink-0 text-slate-400 transition hover:text-emerald-600 disabled:cursor-not-allowed disabled:opacity-50"
        disabled={isPending}
        onClick={onToggle}
        type="button"
      >
        <ToggleLeft size={28} />
      </button>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function ProviderOrderingPanel({ patientId, providerCatalog, providerConfigs }: Props) {
  const queryClient = useQueryClient();

  // Build initial ordered list from catalog + per-patient configs
  function buildRows(
    catalog: CareCircleProvider[],
    configs: CareCircleProviderConfig[],
  ): ProviderRow[] {
    const configMap = new Map(configs.map((c) => [c.provider_key, c]));

    return catalog
      .filter((p) => p.providerKey !== "newsletter_header" && p.providerKey !== "newsletter_footer")
      .map((p) => {
        const cfg = configMap.get(p.providerKey);
        const isEnabled = cfg ? cfg.is_enabled : p.enabled;
        const displayOrder = cfg?.display_order ?? null;
        return {
          providerKey: p.providerKey,
          label: p.label,
          icon: p.icon ?? "",
          category: p.category,
          isEnabled,
          displayOrder: displayOrder ?? 9999,
        };
      });
  }

  const [rows, setRows] = useState<ProviderRow[]>(() => buildRows(providerCatalog, providerConfigs));
  const [saveError, setSaveError] = useState<string | null>(null);

  // Keep in sync when props change (e.g. after invalidation)
  useEffect(() => {
    setRows(buildRows(providerCatalog, providerConfigs));
  }, [providerCatalog, providerConfigs]);

  const enabledRows = [...rows.filter((r) => r.isEnabled)].sort((a, b) => a.displayOrder - b.displayOrder);
  const disabledRows = rows.filter((r) => !r.isEnabled).sort((a, b) => a.label.localeCompare(b.label));

  // ── Reorder mutation ──────────────────────────────────────────────────────

  const reorderMutation = useMutation({
    mutationFn: (ordering: { provider_key: string; display_order: number }[]) =>
      reorderCareCirclePatientProviderConfigs(patientId, ordering),
    onError: () => setSaveError("Could not save the new order. Please try again."),
  });

  function persistOrder(nextEnabled: ProviderRow[]) {
    const ordering = nextEnabled.map((r, i) => ({
      provider_key: r.providerKey,
      display_order: i,
    }));
    reorderMutation.mutate(ordering);
  }

  // ── Toggle mutation ───────────────────────────────────────────────────────

  const toggleMutation = useMutation({
    mutationFn: ({ providerKey, isEnabled }: { providerKey: string; isEnabled: boolean }) =>
      updateCareCirclePatientProviderConfig(patientId, providerKey, {
        is_enabled: isEnabled,
        custom_parameters: {},
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["care-circle-family-patient-provider-configs", patientId] });
      setSaveError(null);
    },
    onError: () => setSaveError("Could not update provider. Please try again."),
  });

  function handleToggle(providerKey: string) {
    const row = rows.find((r) => r.providerKey === providerKey);
    if (!row) return;
    const nextEnabled = !row.isEnabled;

    // Optimistic update
    setRows((prev) =>
      prev.map((r) => (r.providerKey === providerKey ? { ...r, isEnabled: nextEnabled } : r))
    );

    toggleMutation.mutate({ providerKey, isEnabled: nextEnabled });

    // If enabling, append to end of enabled list and persist order
    if (nextEnabled) {
      const nextEnabledRows = [...enabledRows, { ...row, isEnabled: true }];
      persistOrder(nextEnabledRows);
    }
  }

  // ── Drag end ──────────────────────────────────────────────────────────────

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = enabledRows.findIndex((r) => r.providerKey === active.id);
    const newIndex = enabledRows.findIndex((r) => r.providerKey === over.id);
    const nextEnabled = arrayMove(enabledRows, oldIndex, newIndex);

    // Update local display order values
    const updatedRows = rows.map((r) => {
      const pos = nextEnabled.findIndex((e) => e.providerKey === r.providerKey);
      return pos >= 0 ? { ...r, displayOrder: pos } : r;
    });
    setRows(updatedRows);
    persistOrder(nextEnabled);
  }

  // ── Up / Down buttons ─────────────────────────────────────────────────────

  function moveRow(providerKey: string, direction: "up" | "down") {
    const index = enabledRows.findIndex((r) => r.providerKey === providerKey);
    const nextIndex = direction === "up" ? index - 1 : index + 1;
    if (nextIndex < 0 || nextIndex >= enabledRows.length) return;

    const nextEnabled = arrayMove(enabledRows, index, nextIndex);
    const updatedRows = rows.map((r) => {
      const pos = nextEnabled.findIndex((e) => e.providerKey === r.providerKey);
      return pos >= 0 ? { ...r, displayOrder: pos } : r;
    });
    setRows(updatedRows);
    persistOrder(nextEnabled);
  }

  const isPending = reorderMutation.isPending || toggleMutation.isPending;

  return (
    <div className="mt-6 space-y-6">
      {saveError ? (
        <p className="text-sm text-[#a0382b]">{saveError}</p>
      ) : null}

      {/* Enabled providers — sortable */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-[0.24em] text-ink-600">
            Active providers
          </span>
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-800">
            {enabledRows.length}
          </span>
          {isPending ? (
            <span className="ml-auto text-xs text-ink-400">Saving…</span>
          ) : null}
        </div>

        {enabledRows.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-black/10 px-4 py-6 text-center text-sm text-ink-500">
            No providers enabled. Toggle providers below to add them.
          </p>
        ) : (
          <DndContext
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
            sensors={sensors}
          >
            <SortableContext
              items={enabledRows.map((r) => r.providerKey)}
              strategy={verticalListSortingStrategy}
            >
              <div className="space-y-2">
                {enabledRows.map((row, index) => (
                  <SortableProviderRow
                    index={index}
                    isPending={isPending}
                    key={row.providerKey}
                    onMoveDown={() => moveRow(row.providerKey, "down")}
                    onMoveUp={() => moveRow(row.providerKey, "up")}
                    onToggle={() => handleToggle(row.providerKey)}
                    row={row}
                    total={enabledRows.length}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        )}
      </div>

      {/* Disabled providers */}
      {disabledRows.length > 0 ? (
        <div>
          <div className="mb-3 flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-[0.24em] text-ink-500">
              Available (disabled)
            </span>
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-500">
              {disabledRows.length}
            </span>
          </div>
          <div className="space-y-2">
            {disabledRows.map((row) => (
              <DisabledProviderRow
                isPending={isPending}
                key={row.providerKey}
                onToggle={() => handleToggle(row.providerKey)}
                row={row}
              />
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
