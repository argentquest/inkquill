"use client";

import Link from "next/link";
import {
  BookOpen,
  Globe,
  MessageCircle,
  FileText,
  FileUp,
  Wand2,
  BrainCircuit,
  Newspaper,
  CreditCard,
  Gift,
  UserCircle,
  Sparkles,
  Hammer,
} from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { HelpButton } from "@/components/ui/help-modal";
import { storytellingHelp } from "@/lib/help-content";

const productLinks = [
  { href: "/storytelling/stories", label: "Stories", description: "Create, edit, and manage your stories.", icon: BookOpen },
  { href: "/storytelling/worlds", label: "Worlds", description: "Build and explore your story worlds.", icon: Globe },
  { href: "/storytelling/world-builder", label: "World Builder", description: "Generate a world by answering guided questions.", icon: Hammer },
  { href: "/storytelling/documents", label: "Documents", description: "Upload and manage reference documents.", icon: FileUp },
  { href: "/storytelling/community", label: "Community", description: "Discover published works and connect with writers.", icon: MessageCircle },
  { href: "/storytelling/published", label: "Published", description: "View and manage your published stories.", icon: FileText },
  { href: "/storytelling/prompts", label: "Prompts", description: "Browse and manage your writing prompts.", icon: Wand2 },
  { href: "/storytelling/ai-models", label: "AI Models", description: "Explore available AI models and pricing.", icon: BrainCircuit },
  { href: "/storytelling/blog", label: "Blog", description: "Write and publish blog posts.", icon: Newspaper },
];

const commerceLinks = [
  { href: "/storytelling/account", label: "Account", description: "Edit your profile and contact details.", icon: UserCircle },
  { href: "/storytelling/billing", label: "Billing", description: "Review your balance and purchase credits.", icon: CreditCard },
  { href: "/storytelling/referrals", label: "Referrals", description: "Track invitations and earned credits.", icon: Gift },
  { href: "/chatbot", label: "Chatbot", description: "Quick AI chat for research and brainstorming.", icon: Sparkles },
];

function HubCard({
  href,
  label,
  description,
  icon: Icon,
}: {
  href: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Link
      className="flex flex-col gap-3 rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white"
      href={href}
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-ink-900/6">
        <Icon className="h-5 w-5 text-ink-700" />
      </div>
      <div>
        <h2 className="font-semibold text-ink-900">{label}</h2>
        <p className="mt-1 text-sm leading-6 text-ink-600">{description}</p>
      </div>
    </Link>
  );
}

export default function StorytellingPage() {
  const { user, status } = useSession();
  const name = user?.display_name ?? user?.username;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Storytelling"
        title={status === "authenticated" && name ? `Welcome back, ${name}.` : "Storytelling"}
        description="Create worlds, write stories, and share your work with the community."
      />

      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-ink-600">Product</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {productLinks.map((link) => (
            <HubCard key={link.href} {...link} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-ink-600">Account & Tools</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {commerceLinks.map((link) => (
            <HubCard key={link.href} {...link} />
          ))}
        </div>
      </section>

      <HelpButton helpContent={storytellingHelp} position="bottom-right" />
    </div>
  );
}
