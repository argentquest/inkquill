import type { Metadata } from "next";
import { EB_Garamond, Lora } from "next/font/google";

import "@/app/globals.css";
import { AppProviders } from "@/components/providers/app-providers";
import { CookieConsentBanner } from "@/components/shell/cookie-consent-banner";
import { MaintenanceBanner } from "@/components/shell/maintenance-banner";
import { ToastCenter } from "@/components/ui/toast-center";

const ebGaramond = EB_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-display",
  display: "swap",
});

const lora = Lora({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Ink & Quill",
  description: "Care Circle — a thoughtful platform for family and friend care coordination."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${ebGaramond.variable} ${lora.variable}`}>
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
