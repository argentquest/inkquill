"use client";

import { useParams } from "next/navigation";
import { ChatbotWorkspace } from "@/components/chatbot/chatbot-workspace";

export default function ChatbotSessionDetailPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = Number(params.sessionId);

  return <ChatbotWorkspace initialSessionId={sessionId} />;
}