"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { Loader2, ArrowLeft } from "lucide-react";
import Link from "next/link";

import { fetchCareCircleProviders } from "@/lib/api";
import { PageHeader } from "@/components/shell/page-header";

export default function ProviderDetailPage() {
  const params = useParams();
  const providerKey = params?.providerKey as string;

  const { data: providers, isLoading, isError } = useQuery({
    queryKey: ["care-circle", "providers"],
    queryFn: fetchCareCircleProviders
  });

  const provider = providers?.find((p) => p.providerKey === providerKey);

  if (isLoading) {
    return (
      <div className="flex h-32 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError || !provider) {
    return (
      <div className="space-y-6">
        <Link 
          className="inline-flex items-center gap-2 text-sm font-semibold text-ink-500 hover:text-ink-900" 
          href="/care-circle-family/providers"
        >
          <ArrowLeft className="size-4" />
          Back to Providers
        </Link>
        <div className="rounded-[28px] border border-red-200 bg-red-50 p-6 shadow-panel">
          <p className="text-sm font-semibold text-red-800">
            {isError ? "Failed to load provider data." : "Provider not found."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <Link 
        className="inline-flex items-center gap-2 text-sm font-semibold text-ink-500 hover:text-ink-900" 
        href="/care-circle-family/providers"
      >
        <ArrowLeft className="size-4" />
        Back to Providers
      </Link>
      
      <PageHeader
        description={`Manage operational parameters and visibility testing for the ${provider.label} provider output.`}
        eyebrow="Provider Details"
        title={`${provider.icon || "📰"} ${provider.label}`}
      />

      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel text-sm">
          <h3 className="text-base font-bold text-ink-900">Provider Specifications</h3>
          <ul className="mt-4 space-y-4 text-ink-700">
            <li className="flex justify-between border-b pb-2">
              <span className="font-semibold text-ink-900">Technical Key</span>
              <span className="font-mono text-xs">{provider.providerKey}</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="font-semibold text-ink-900">Module Category</span>
              <span className="capitalize">{provider.category}</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="font-semibold text-ink-900">System Visibility</span>
              <span>{provider.enabled ? "Active" : "Disabled"}</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="font-semibold text-ink-900">Patient Visibility</span>
              <span>{provider.patientVisible ? "Safe for Direct Display" : "Family Access Only"}</span>
            </li>
          </ul>
        </section>

        <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel text-sm flex flex-col items-center justify-center text-center">
            <h3 className="mb-2 text-base font-bold text-ink-900">Test Generation Diagnostics</h3>
            <p className="mb-4 text-ink-500">
              Diagnostic preview and explicit patient mapping controls will be routed here upon further sprint integrations.
            </p>
            <div className="inline-flex rounded-full bg-slate-100 px-4 py-2 font-mono text-xs text-slate-500">
              Awaiting Playwright Verification Loop
            </div>
        </section>
      </div>
    </div>
  );
}
