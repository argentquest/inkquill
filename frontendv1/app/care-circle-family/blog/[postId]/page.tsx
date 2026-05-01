"use client";

import { BlogPostEditor } from "@/components/blog/blog-post-editor";
import { useParams } from "next/navigation";

export default function CareCircleEditBlogPostPage() {
  const params = useParams();
  const postId = Number(params.postId);
  return <BlogPostEditor appSource="care-circle" basePath="/care-circle-family/blog" postId={postId} />;
}
