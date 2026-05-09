"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { SectionHeading } from "@/components/shell/section-heading";
import { HubSidebar } from "@/components/shell/hub-sidebar";
import { HelpButton } from "@/components/ui/help-modal";
import { careCircleFamilyHelp } from "@/lib/help-content";
import { fetchBlogPosts, fetchForumThreads } from "@/lib/api";
import {
  FriendsIcon,
  MembersIcon,
  ActivityIcon,
  MediaIcon,
  ProvidersIcon,
  BlogIcon,
  ForumsIcon,
  ChatbotIcon,
  AccountIcon,
  ReferralsIcon,
  BillingIcon,
  AdminIcon,
  SchedulerIcon,
  TemplateStudioIcon,
  FamiliesIcon,
} from "@/components/care-circle-family/care-circle-feature-icons";

interface HubCard {
  href: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const careGroup: HubCard[] = [
  {
    href: "/care-circle-family/patients",
    label: "Friends",
    description: "View and manage all friend profiles.",
    icon: FriendsIcon,
  },
  {
    href: "/care-circle-family/members",
    label: "Members",
    description: "Manage family circle access and invitations.",
    icon: MembersIcon,
  },
  {
    href: "/care-circle-family/events",
    label: "Recent Activity",
    description: "Monitor recent session and engagement events.",
    icon: ActivityIcon,
  },
  {
    href: "/care-circle-family/media",
    label: "Media",
    description: "Upload family photos for personalised prompts.",
    icon: MediaIcon,
  },
  {
    href: "/care-circle-family/providers",
    label: "Providers",
    description: "Configure content providers for daily sessions.",
    icon: ProvidersIcon,
  },
];

const communityGroup: HubCard[] = [
  {
    href: "/care-circle-family/blog",
    label: "Blog",
    description: "Write and publish circle-facing blog posts.",
    icon: BlogIcon,
  },
  {
    href: "/community/forums",
    label: "Forums",
    description: "Join discussions with the care circle community.",
    icon: ForumsIcon,
  },
  {
    href: "/chatbot",
    label: "Chatbot",
    description: "Quick AI chat for research and brainstorming.",
    icon: ChatbotIcon,
  },
];

const accountGroup: HubCard[] = [
  {
    href: "/care-circle-family/account",
    label: "Account",
    description: "Edit your profile and family settings.",
    icon: AccountIcon,
  },
  {
    href: "/care-circle-family/referrals",
    label: "Referrals",
    description: "Track invitations and earned credits.",
    icon: ReferralsIcon,
  },
];

const adminGroup: HubCard[] = [
  {
    href: "/care-circle-family/admin",
    label: "Admin Dashboard",
    description: "Manage families, users, and platform settings.",
    icon: AdminIcon,
  },
  {
    href: "/care-circle-family/admin/scheduler",
    label: "Scheduler",
    description: "Configure cron jobs and task scheduling.",
    icon: SchedulerIcon,
  },
  {
    href: "/care-circle-family/admin/template-studio",
    label: "Template Studio",
    description: "Design provider templates with GrapesJS.",
    icon: TemplateStudioIcon,
  },
  {
    href: "/care-circle-family/admin/families",
    label: "Families",
    description: "Review and manage all care circle families.",
    icon: FamiliesIcon,
  },
];

const accountingGroup: HubCard[] = [
  {
    href: "/care-circle-family/billing",
    label: "Billing",
    description: "Review balance, invoices, and purchase credits.",
    icon: BillingIcon,
  },
];

function FeatureCard({ href, label, description, icon: Icon }: HubCard) {
  return (
    <Link
      href={href}
      data-testid={`hub-card-${label.toLowerCase().replace(/\s+/g, "-")}`}
      className="group flex flex-col gap-4 rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-ink-900/6 text-ink-700">
        <Icon className="h-9 w-9" />
      </div>
      <div className="flex-1">
        <h3 className="font-semibold text-ink-900">{label}</h3>
        <p className="mt-1 text-sm leading-6 text-ink-600">{description}</p>
      </div>
      <ArrowRight className="size-4 text-ink-400 transition group-hover:translate-x-0.5 group-hover:text-ink-700" />
    </Link>
  );
}

export default function CareCircleFamilyPage() {
  const session = useSession();
  const { user } = session;
  const name = user?.display_name ?? user?.username;
  const isAdmin = user?.is_admin === true;

  const { data: blogPosts = [] } = useQuery({
    queryKey: ["care-circle-blog-posts", "care-circle"],
    queryFn: () => fetchBlogPosts({ app_source: "care-circle" }),
  });

  const { data: forumThreads = [] } = useQuery({
    queryKey: ["care-circle-forum-threads", "care-circle"],
    queryFn: () => fetchForumThreads({ app_source: "care-circle" }),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Care Circle Family"
        title={name ? `Welcome back, ${name}.` : "Care Circle Family"}
        description="Manage your care circle, contribute to daily editions, and stay connected with family."
      />

      <div className="flex items-start gap-6">
        <div className="min-w-0 flex-1 space-y-8">
          <section className="space-y-4">
            <SectionHeading
              title="Care & Circle"
              meta="Section A"
              action={{ label: "Manage all", href: "/care-circle-family/members" }}
            />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {careGroup.map((card) => (
                <FeatureCard key={card.href} {...card} />
              ))}
            </div>
          </section>

          <section className="space-y-4">
            <SectionHeading
              title="Community"
              meta="Section B"
              action={{ label: "All threads", href: "/community/forums" }}
            />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {communityGroup.map((card) => (
                <FeatureCard key={card.href} {...card} />
              ))}
            </div>
          </section>

          <section className="space-y-4">
            <SectionHeading title="Account" />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {accountGroup.map((card) => (
                <FeatureCard key={card.href} {...card} />
              ))}
            </div>
          </section>

          {isAdmin && (
            <section className="space-y-4">
              <SectionHeading title="Admin" />
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {adminGroup.map((card) => (
                  <FeatureCard key={card.href} {...card} />
                ))}
              </div>
            </section>
          )}

          <section className="space-y-4">
            <SectionHeading title="Accounting" />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {accountingGroup.map((card) => (
                <FeatureCard key={card.href} {...card} />
              ))}
            </div>
          </section>
        </div>

        <div className="hidden w-72 shrink-0 xl:block">
          <HubSidebar
            blogPosts={blogPosts}
            forumThreads={forumThreads}
            blogHref="/care-circle-family/blog"
            forumHref="/community/forums"
          />
        </div>
      </div>

      <HelpButton helpContent={careCircleFamilyHelp} position="bottom-right" />
    </div>
  );
}
