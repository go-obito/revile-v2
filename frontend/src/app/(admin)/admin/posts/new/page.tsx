"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { PostForm } from "@/components/PostForm";
import type { PostFormValues } from "@/components/PostForm";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function NewPostPage() {
  const { accessToken, hasRole } = useAuth();
  const router = useRouter();
  const [error, setError] = useState("");
  async function submit(values: PostFormValues, publish: boolean) {
    if (!accessToken) return;
    setError("");
    try { const post = await api.createPost({ ...values, dek: values.dek || null }, accessToken); if (publish) await api.publishPost(post.id, accessToken); router.push("/admin/posts"); } catch (submitError) { setError(submitError instanceof Error ? submitError.message : "Unable to save post."); }
  }
  return <main className="admin-content narrow-content"><p className="eyebrow">New dispatch</p><h1>Write the story.</h1><PostForm onSubmit={submit} canPublish={hasRole("admin", "editor")} submitLabel="Save draft" submittingLabel="Saving..." error={error} /></main>;
}
