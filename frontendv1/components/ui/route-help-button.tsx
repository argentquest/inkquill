"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";

import { HelpButton } from "@/components/ui/help-modal";
import { resolveHelpContent } from "@/lib/help-content";

export function RouteHelpButton() {
  const pathname = usePathname();
  const [hasExplicitHelp, setHasExplicitHelp] = useState(false);
  const helpContent = useMemo(() => resolveHelpContent(pathname ?? "/"), [pathname]);

  useEffect(() => {
    const syncExplicitHelp = () => {
      const explicitHelpTriggers = Array.from(document.querySelectorAll<HTMLElement>("[data-page-help-trigger='true']"))
        .filter((element) => !element.closest("[data-global-route-help='true']"));

      setHasExplicitHelp(explicitHelpTriggers.length > 0);
    };

    syncExplicitHelp();

    const observer = new MutationObserver(() => {
      syncExplicitHelp();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["data-page-help-trigger"]
    });

    return () => observer.disconnect();
  }, [pathname]);

  if (hasExplicitHelp) {
    return null;
  }

  return (
    <div data-global-route-help="true">
      <HelpButton helpContent={helpContent} position="bottom-right" />
    </div>
  );
}
