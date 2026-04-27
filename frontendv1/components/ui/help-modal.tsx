"use client";

import { useState } from "react";
import { HelpCircle, X } from "lucide-react";

interface HelpItem {
  title: string;
  content: string;
}

interface HelpSection {
  title: string;
  items: HelpItem[];
}

export interface PageHelpContent {
  title: string;
  description: string;
  sections: HelpSection[];
}

/**
 * HelpModal - A modal dialog that displays contextual help content for a page.
 * 
 * @param helpContent - The structured help content to display
 * @param triggerLabel - Optional label for the help trigger button (default: "Help")
 * @param size - Modal size: "default" | "large"
 */
export function HelpModal({
  helpContent,
  triggerLabel = "Help",
  size = "default"
}: {
  helpContent: PageHelpContent;
  triggerLabel?: string;
  size?: "default" | "large";
}) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm text-ink-600 transition hover:bg-black/5 hover:text-ink-900"
        data-page-help-trigger="true"
        title={`Open help for ${helpContent.title}`}
      >
        <HelpCircle className="size-4" />
        <span>{triggerLabel}</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-ink-900/50 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
          />

          {/* Modal */}
          <div
            className={`
              relative z-10 max-h-[85vh] overflow-y-auto rounded-[28px] border border-black/10 bg-paper p-6 shadow-panel
              ${size === "large" ? "w-full max-w-3xl" : "w-full max-w-lg"}
            `}
          >
            {/* Header */}
            <div className="mb-6 flex items-start justify-between">
              <div>
                <h2 className="font-display text-2xl text-ink-900">{helpContent.title}</h2>
                <p className="mt-1.5 text-sm text-ink-600">{helpContent.description}</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="shrink-0 rounded-full p-2 text-ink-400 transition hover:bg-black/5 hover:text-ink-900"
                aria-label="Close help"
              >
                <X className="size-5" />
              </button>
            </div>

            {/* Content sections */}
            <div className="space-y-6">
              {helpContent.sections.map((section, sectionIndex) => (
                <div key={sectionIndex}>
                  <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-forest">
                    {section.title}
                  </h3>
                  <div className="space-y-3">
                    {section.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="rounded-xl bg-white/50 p-4">
                        <h4 className="font-medium text-ink-900">{item.title}</h4>
                        <p className="mt-1 text-sm text-ink-700 leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="mt-8 flex justify-center">
              <button
                onClick={() => setIsOpen(false)}
                className="inline-flex items-center justify-center rounded-full border border-black/10 bg-white/80 px-5 py-3 text-sm font-semibold text-ink-900 transition hover:bg-white"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/**
 * HelpButton - A simple floating help button that triggers a help modal.
 * Use this for pages where you want a floating help button in the corner.
 */
export function HelpButton({
  helpContent,
  position = "bottom-right"
}: {
  helpContent: PageHelpContent;
  position?: "bottom-right" | "bottom-left" | "top-right" | "top-left";
}) {
  const [isOpen, setIsOpen] = useState(false);

  const positionClasses = {
    "bottom-right": "bottom-6 right-6",
    "bottom-left": "bottom-6 left-6",
    "top-right": "top-6 right-6",
    "top-left": "top-6 left-6"
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={`
          fixed z-40 flex size-12 items-center justify-center rounded-full
          bg-forest text-paper shadow-lg transition hover:bg-forest/90 hover:scale-105
          ${positionClasses[position]}
        `}
        aria-label="Open help"
        data-page-help-trigger="true"
        title={`Open help for ${helpContent.title}`}
      >
        <HelpCircle className="size-5" />
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-ink-900/50 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
          />

          {/* Modal */}
          <div className="relative z-10 max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-[28px] border border-black/10 bg-paper p-6 shadow-panel">
            {/* Header */}
            <div className="mb-6 flex items-start justify-between">
              <div>
                <h2 className="font-display text-2xl text-ink-900">{helpContent.title}</h2>
                <p className="mt-1.5 text-sm text-ink-600">{helpContent.description}</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="shrink-0 rounded-full p-2 text-ink-400 transition hover:bg-black/5 hover:text-ink-900"
                aria-label="Close help"
              >
                <X className="size-5" />
              </button>
            </div>

            {/* Content sections */}
            <div className="space-y-6">
              {helpContent.sections.map((section, sectionIndex) => (
                <div key={sectionIndex}>
                  <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-forest">
                    {section.title}
                  </h3>
                  <div className="space-y-3">
                    {section.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="rounded-xl bg-white/50 p-4">
                        <h4 className="font-medium text-ink-900">{item.title}</h4>
                        <p className="mt-1 text-sm text-ink-700 leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="mt-8 flex justify-center">
              <button
                onClick={() => setIsOpen(false)}
                className="inline-flex items-center justify-center rounded-full border border-black/10 bg-white/80 px-5 py-3 text-sm font-semibold text-ink-900 transition hover:bg-white"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
