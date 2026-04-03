import type { Metadata } from "next";

import "@/app/globals.css";
import { AppProviders } from "@/components/providers/app-providers";
import { CookieConsentBanner } from "@/components/shell/cookie-consent-banner";
import { MaintenanceBanner } from "@/components/shell/maintenance-banner";
import { ToastCenter } from "@/components/ui/toast-center";

export const metadata: Metadata = {
  title: "Ink & Quill Frontend V1",
  description: "Sprint 1 foundation and shell for the React rebuild."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AppProviders>
          <MaintenanceBanner />
          {children}
          <ToastCenter />
          <CookieConsentBanner />
        </AppProviders>
      </body>
    </html>
  );
}
