"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { PostForm } from "@/components/PostForm";
import type { PostFormValues } from "@/components/PostForm";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function NewPostPage() {
  const { accessToken } = useAuth();
  const router = useRouter();
  const [error, setError] = useState("");
  async function submit(values: PostFormValues) {
    if (!accessToken) return;
    setError("");
    try { await api.createPost({ ...values, dek: values.dek || null }, accessToken); router.push("/admin/posts"); } catch (submitError) { setError(submitError instanceof Error ? submitError.message : "Unable to save post."); }
  }
  return <main className="admin-content narrow-content"><p className="eyebrow">New dispatch</p><h1>Write the story.</h1><PostForm onSubmit={submit} submitLabel="Save draft" submittingLabel="Saving..." error={error} /></main>;
}
