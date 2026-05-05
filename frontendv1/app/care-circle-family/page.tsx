"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { FileText, MessageSquare, ArrowRight } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { HelpButton } from "@/components/ui/help-modal";
import { careCircleFamilyHelp } from "@/lib/help-content";
import { fetchBlogPosts, fetchForumThreads } from "@/lib/api";
import type { BlogPost, ForumThreadSummary } from "@/lib/api";
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

function SectionHeader({ title }: { title: string }) {
  return (
    <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-ink-600">
      {title}
    </h2>
  );
}

function FeatureCard({ href, label, description, icon: Icon }: HubCard) {
  return (
    <Link
      key={href}
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

function RecentSection({
  title,
  icon,
  children,
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  const testId = title.toLowerCase().replace(/\s+/g, "-");
  return (
    <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel" data-testid={testId}>
      <div className="flex items-center gap-2 text-sm font-semibold text-ink-900">
        {icon}
        {title}
      </div>
      <div className="mt-4 space-y-3">{children}</div>
    </section>
  );
}

function BlogRow({ post }: { post: BlogPost }) {
  return (
    <Link
      className="block rounded-2xl border border-black/10 bg-white/70 p-4 transition hover:border-black/20"
      href={`/public/blog/${post.slug}`}
    >
      <p className="text-sm font-semibold text-ink-900">{post.title}</p>
      <p className="mt-1 text-xs text-ink-500">
        {post.comment_count} comments · {post.view_count.toLocaleString()} views
      </p>
    </Link>
  );
}

function ForumRow({ thread }: { thread: ForumThreadSummary }) {
  return (
    <Link
      className="block rounded-2xl border border-black/10 bg-white/70 p-4 transition hover:border-black/20"
      href={`/community/forums/${thread.id}`}
    >
      <p className="text-sm font-semibold text-ink-900">{thread.title}</p>
      <p className="mt-1 text-xs text-ink-500">
        {thread.category_name ?? "Forum"} · {thread.post_count} replies
      </p>
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
      {name && (
        <p className="text-sm text-ink-600">
          Welcome back, <span className="font-semibold text-ink-900">{name}</span>. Use the navigation above to manage your circle.
        </p>
      )}

      <section className="space-y-4">
        <SectionHeader title="Care &amp; Circle" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {careGroup.map((card) => (
            <FeatureCard key={card.href} {...card} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeader title="Community" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {communityGroup.map((card) => (
            <FeatureCard key={card.href} {...card} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeader title="Account" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {accountGroup.map((card) => (
            <FeatureCard key={card.href} {...card} />
          ))}
        </div>
      </section>

      {isAdmin && (
        <section className="space-y-4">
          <SectionHeader title="Admin" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {adminGroup.map((card) => (
              <FeatureCard key={card.href} {...card} />
            ))}
          </div>
        </section>
      )}

      <section className="space-y-4">
        <SectionHeader title="Accounting" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {accountingGroup.map((card) => (
            <FeatureCard key={card.href} {...card} />
          ))}
        </div>
      </section>

      {(blogPosts.length > 0 || forumThreads.length > 0) && (
        <section className="grid gap-6 xl:grid-cols-2">
          {blogPosts.length > 0 && (
            <RecentSection
              title="Recent Blog Posts"
              icon={<FileText className="size-4 text-ink-500" />}
            >
              {blogPosts.slice(0, 5).map((post) => (
                <BlogRow key={post.id} post={post} />
              ))}
            </RecentSection>
          )}
          {forumThreads.length > 0 && (
            <RecentSection
              title="Recent Forum Posts"
              icon={<MessageSquare className="size-4 text-ink-500" />}
            >
              {forumThreads.slice(0, 5).map((thread) => (
                <ForumRow key={thread.id} thread={thread} />
              ))}
            </RecentSection>
          )}
        </section>
      )}

      <HelpButton helpContent={careCircleFamilyHelp} position="bottom-right" />
    </div>
  );
}
