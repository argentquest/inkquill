import { ChatbotWorkspace } from "@/components/chatbot/chatbot-workspace";
import { PageHeader } from "@/components/shell/page-header";
import { HelpButton } from "@/components/ui/help-modal";
import { chatbotHelp } from "@/lib/help-content";

export default function ChatbotPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Chatbot"
        title="Your AI assistant"
        description="Ask anything, brainstorm ideas, or get quick answers — a focused AI chat workspace."
      />
      <ChatbotWorkspace />
      <HelpButton helpContent={chatbotHelp} position="bottom-right" />
    </div>
  );
}
