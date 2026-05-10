"use client";

import Link from "next/link";
import { useLayoutEffect } from "react";
import { CreditCard, Megaphone, MessageSquare, Settings2, ShieldCheck, Tags, Users, Wrench } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { LoadingState } from "@/components/ui/loading-state";

const adminSections = [
  {
    href: "/admin/forums",
    label: "Forum Categories",
    description: "Add, edit, enable, and disable forum categories for Storytelling and Care Circle apps.",
    icon: MessageSquare,
  },
  {
    href: "/admin/users",
    label: "Users",
    description: "View all users, toggle active/inactive status, and inspect account details.",
    icon: Users,
  },
  {
    href: "/admin/billing",
    label: "Billing",
    description: "Monitor system billing stats, review recent transactions, and adjust user credits manually.",
    icon: CreditCard,
  },
  {
    href: "/admin/cta",
    label: "CTA Content",
    description: "Manage call-to-action blocks across the platform. Toggle active status or delete entries.",
    icon: Megaphone,
  },
  {
    href: "/admin/maintenance",
    label: "Maintenance Mode",
    description: "Enable or disable site-wide maintenance mode with a custom message and duration.",
    icon: Wrench,
  },
  {
    href: "/care-circle-family/admin",
    label: "Care Circle Admin",
    description: "Manage Care Circle families, scheduler jobs, and provider template studio.",
    icon: Settings2,
  },
  {
    href: "/admin/tag-taxonomy",
    label: "Tag Taxonomy",
    description: "Manage the categorized word suggestions shown when editing friend profiles — hobbies, activities, life roles, foods, TV shows, and more.",
    icon: Tags,
  },
];

export default function AdminHubPage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace("/auth/login?next=/admin");
    } else if (session.status === "authenticated" && !isAdmin) {
      window.location.replace("/access-denied?surface=admin");
    }
  }, [session.status, isAdmin]);

  if (session.status === "loading" || (session.status === "authenticated" && !isAdmin)) {
    return <LoadingState label="Checking access" />;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Administration"
        title="Platform Admin"
        description="System-wide tools restricted to admin users. Changes here affect all users and content across the platform."
        action={
          <div className="flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-800">
            <ShieldCheck className="h-4 w-4" />
            Admin only
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" data-testid="admin-hub-grid">
        {adminSections.map(({ href, label, description, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className="flex flex-col gap-3 rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white"
            data-testid="admin-hub-card"
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
