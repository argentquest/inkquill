import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { ProviderTemplateStudio } from "@/components/care-circle-family/provider-template-studio";
import { PageHeader } from "@/components/shell/page-header";

export default function CareCircleTemplateStudioPage() {
  return (
    <div className="space-y-8">
      <Link
        className="inline-flex items-center gap-2 text-sm font-semibold text-ink-500 hover:text-ink-900"
        href="/care-circle-family/providers"
      >
        <ArrowLeft className="size-4" />
        Back to providers
      </Link>

      <PageHeader
        eyebrow="Admin Template Studio"
        title="Care Circle Provider Templates"
        description="Edit provider `default.html` files with GrapesJS and save provider-local theme overrides for the selected shared theme."
      />

      <ProviderTemplateStudio />
    </div>
  );
}
