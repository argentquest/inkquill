"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Loader2 } from "lucide-react";

import { fetchCareCircleProviders } from "@/lib/api";
import { PageHeader } from "@/components/shell/page-header";

export default function ProvidersPage() {
  const { data: providers, isLoading, isError } = useQuery({
    queryKey: ["care-circle", "providers"],
    queryFn: fetchCareCircleProviders
  });

  return (
    <div className="space-y-8">
      <PageHeader
        description="Review and configure the content providers available to generate daily active highlights and memory exercises for the patient session."
        eyebrow="Provider Registry"
        title="Content Providers"
      />

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <div className="rounded-[28px] border border-red-200 bg-red-50 p-6 shadow-panel">
          <p className="text-sm font-semibold text-red-800">Failed to load the provider registry.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {providers?.map((provider) => (
            <Link
              key={provider.providerKey}
              className="flex items-center gap-4 rounded-[28px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white"
              href={`/care-circle-family/providers/${provider.providerKey}`}
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-paper text-2xl shadow-sm">
                {provider.icon || "📰"}
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="truncate font-semibold text-ink-900">{provider.label}</h3>
                <div className="mt-1 flex items-center gap-2">
                  <span className="inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-800 capitalize">
                    {provider.category}
                  </span>
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      provider.enabled
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {provider.enabled ? "Active" : "Disabled"}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
