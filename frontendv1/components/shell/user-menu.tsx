"use client";

import Link from "next/link";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ChevronDown, LogOut, UserRound } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { useSession, useToasts } from "@/components/providers/app-providers";
import { getAppAccountBase } from "@/lib/apps";
import { logoutUser } from "@/lib/api";

export function UserMenu() {
  const router = useRouter();
  const pathname = usePathname();
  const { pushToast } = useToasts();
  const session = useSession();
  const { setAnonymous, status, user } = session;
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const accountBase = getAppAccountBase(pathname);
  const accountHref = accountBase;
  const accountEditHref = `${accountBase}/edit`;

  if (status !== "authenticated" || !user) {
    return (
      <Link
        className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/80 px-4 py-2 text-sm text-ink-800 transition hover:border-black/20 hover:bg-white"
        href="/auth/login"
      >
        <UserRound className="h-4 w-4" />
        <span>Sign In</span>
      </Link>
    );
  }

  async function handleLogout() {
    setIsLoggingOut(true);
    try {
      await logoutUser();
      setAnonymous();
      pushToast({ title: "Logged out", tone: "success", detail: "Your session has ended cleanly." });
      router.push("/auth/login");
    } catch (error) {
      pushToast({
        title: "Logout failed",
        tone: "error",
        detail: error instanceof Error ? error.message : "Unable to log out right now."
      });
      setIsLoggingOut(false);
    }
  }

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/80 px-4 py-2 text-sm text-ink-800 transition hover:border-black/20 hover:bg-white"
          type="button"
        >
          <UserRound className="h-4 w-4" />
          <span>{user.display_name ?? user.username}</span>
          <ChevronDown className="h-4 w-4" />
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          className="z-50 min-w-56 rounded-[20px] border border-black/10 bg-paper p-2 shadow-panel"
          sideOffset={8}
        >
          <DropdownMenu.Label className="px-3 py-2 text-xs uppercase tracking-[0.24em] text-ink-600">
            Signed In
          </DropdownMenu.Label>
          <DropdownMenu.Item asChild>
            <Link className="block rounded-xl px-3 py-2 text-sm outline-none hover:bg-black/5" href={accountHref}>
              Account
            </Link>
          </DropdownMenu.Item>
          <DropdownMenu.Item asChild>
            <Link className="block rounded-xl px-3 py-2 text-sm outline-none hover:bg-black/5" href={accountEditHref}>
              Edit profile
            </Link>
          </DropdownMenu.Item>
          <DropdownMenu.Item className="rounded-xl px-3 py-2 text-sm text-ink-600 outline-none">
            {user.email}
          </DropdownMenu.Item>
          <DropdownMenu.Separator className="my-2 h-px bg-black/10" />
          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-sm text-ink-800 outline-none hover:bg-black/5"
            disabled={isLoggingOut}
            onSelect={(event) => {
              event.preventDefault();
              void handleLogout();
            }}
          >
            <LogOut className="h-4 w-4" />
            {isLoggingOut ? "Logging out..." : "Log out"}
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
