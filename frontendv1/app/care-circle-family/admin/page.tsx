"use client";

import Link from "next/link";
import { useLayoutEffect } from "react";
import { Paintbrush, ShieldCheck } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { LoadingState } from "@/components/ui/loading-state";

const adminTools = [
  {
    href: "/care-circle-family/admin/template-studio",
    label: "Template Studio",
    description: "Edit provider HTML templates and per-theme CSS overrides using the GrapesJS visual editor.",
    icon: Paintbrush,
  },
];

export default function AdminHomePage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace(`/auth/login?next=/care-circle-family/admin`);
    } else if (session.status === "authenticated" && !isAdmin) {
      window.location.replace("/access-denied?surface=care-circle-family");
    }
  }, [session.status, isAdmin]);

  if (session.status === "loading" || (session.status === "authenticated" && !isAdmin)) {
    return <LoadingState label="Checking access" />;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Administration"
        title="Care Circle Admin"
        description="Platform tools restricted to admin users. Changes made here affect all families and friends across the system."
        action={
          <div className="flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-800">
            <ShieldCheck className="h-4 w-4" />
            Admin only
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {adminTools.map(({ href, label, description, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className="flex flex-col gap-3 rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-ink-900/6">
              <Icon className="h-5 w-5 text-ink-700" />
            </div>
            <div>
              <h2 className="font-semibold text-ink-900">{label}</h2>
              <p className="mt-1 text-sm leading-6 text-ink-600">{description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
