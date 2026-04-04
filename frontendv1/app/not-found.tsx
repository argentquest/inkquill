import Link from "next/link";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <EmptyState
        eyebrow="Not found"
        action={
          <Link href="/">
            <Button variant="primary">Return home</Button>
          </Link>
        }
        description="The page you're looking for doesn't exist or has been moved."
        title="404 - Page not found"
      />
    </div>
  );
}
