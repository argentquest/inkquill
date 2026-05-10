import { redirect } from "next/navigation";

export default function CareCircleForumAdminRedirect() {
  redirect("/admin/forums?app_source=care-circle");
}
