import { ChatbotWorkspace } from "@/components/chatbot/chatbot-workspace";
import { PageHeader } from "@/components/shell/page-header";

export default function ChatbotPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Chatbot becomes the third application on the shared platform and the first one delivered as a clean chat-first UI."
        eyebrow="Chatbot"
        title="A narrow conversation surface before deeper app work."
      />
      <ChatbotWorkspace />
    </div>
  );
}
