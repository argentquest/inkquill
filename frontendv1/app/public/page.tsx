import { PageHeader } from "@/components/shell/page-header";
import { EmptyState } from "@/components/ui/empty-state";
import { HelpButton } from "@/components/ui/help-modal";
import { publicPageHelp } from "@/lib/help-content";

export default function PublicPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="This route proves the public layout, shared top navigation, footer, and page header pattern work independently from authenticated workspace surfaces."
        eyebrow="Public Shell"
        title="Public-facing routes keep the same voice without copying the app workspace."
      />
      <EmptyState
        description="Content rails, public worlds, and published stories can land here in later sprints without changing the shared shell primitives."
        eyebrow="Empty State"
        title="This surface is intentionally sparse in Sprint 1."
      />
      <HelpButton helpContent={publicPageHelp} position="bottom-right" />
    </div>
  );
}
