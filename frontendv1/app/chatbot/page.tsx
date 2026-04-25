import { ChatbotWorkspace } from "@/components/chatbot/chatbot-workspace";
import { PageHeader } from "@/components/shell/page-header";
import { HelpButton } from "@/components/ui/help-modal";
import { chatbotHelp } from "@/lib/help-content";

export default function ChatbotPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Chatbot becomes the third application on the shared platform and the first one delivered as a clean chat-first UI."
        eyebrow="Chatbot"
        title="A narrow conversation surface before deeper app work."
      />
      <ChatbotWorkspace />
      <HelpButton helpContent={chatbotHelp} position="bottom-right" />
    </div>
  );
}
