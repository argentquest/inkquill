"use client";

import { ImageIcon } from "lucide-react";
import { PageHeader } from "@/components/shell/page-header";

export default function FamilyMediaLibraryPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Upload and arrange the photographs that power personalized patient memory prompts such as 'Memory Lane Photo' and 'Dog Photo'."
        eyebrow="Media Library"
        title="Family Uploads & Pictures"
      />

      <section className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
          <ImageIcon className="size-8" />
        </div>
        <h3 className="mt-4 text-base font-bold text-ink-900">No media uploaded yet</h3>
        <p className="mt-2 text-sm text-ink-500 max-w-sm">
          Family members can upload classic photographs here. These will be securely mapped and parsed by the localized generative AI model to build calm daily patient prompts.
        </p>
        <button className="mt-6 rounded-full bg-ink-900 px-6 py-2.5 text-sm font-semibold text-paper transition hover:bg-ink-700">
          Upload Photos
        </button>
      </section>
    </div>
  );
}
