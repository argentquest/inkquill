import { LoadingState } from "@/components/ui/loading-state";

export default function Loading() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 md:px-6">
      <LoadingState label="Loading route" />
    </main>
  );
}
