"use client";

import Link from "next/link";
import { Users, Puzzle, CreditCard, Gift, UserCircle, Camera, Activity, UserCheck, UserPlus } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";

const ownerLinks = [
  { href: "/care-circle-family/patients", label: "Friends", description: "View and manage all friend profiles.", icon: Users },
  { href: "/care-circle-family/providers", label: "Providers", description: "Configure content providers for daily highlights.", icon: Puzzle },
  { href: "/care-circle-family/billing", label: "Billing", description: "Review your balance and transaction history.", icon: CreditCard },
  { href: "/care-circle-family/referrals", label: "Referrals", description: "Track invitations and earned credits.", icon: Gift },
  { href: "/care-circle-family/account", label: "Account", description: "Edit your profile and contact details.", icon: UserCircle },
  { href: "/care-circle-family/media", label: "Media", description: "Upload family photos for personalised prompts.", icon: Camera },
  { href: "/care-circle-family/events", label: "Activity", description: "Monitor recent session and engagement events.", icon: Activity },
  { href: "/care-circle-family/members", label: "Members", description: "Approve join requests and manage family members.", icon: UserPlus },
  { href: "/care-circle-patient/login", label: "Friend sign-in", description: "Preview the picture-based sign-in flow.", icon: UserCheck },
];

const memberLinks = [
  { href: "/care-circle-family/patients", label: "Friends", description: "View all friend profiles in this care circle.", icon: Users },
  { href: "/care-circle-family/providers", label: "Providers", description: "View content providers for daily highlights.", icon: Puzzle },
  { href: "/care-circle-family/account", label: "Account", description: "Edit your profile and contact details.", icon: UserCircle },
  { href: "/care-circle-patient/login", label: "Friend sign-in", description: "Preview the picture-based sign-in flow.", icon: UserCheck },
];

export default function CareCircleFamilyPage() {
  const { user, status } = useSession();
  const isOwner = user?.is_family_owner === true;
  const links = isOwner ? ownerLinks : memberLinks;
  const name = user?.display_name ?? user?.username;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Care Circle"
        title={status === "authenticated" && name ? `Welcome back, ${name}.` : "Care Circle"}
        description={
          isOwner
            ? "You own this Care Circle. Manage friends, providers, billing, and account settings below."
            : "You are a member of this Care Circle. View and manage friend profiles and providers below."
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {links.map(({ href, label, description, icon: Icon }) => (
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
