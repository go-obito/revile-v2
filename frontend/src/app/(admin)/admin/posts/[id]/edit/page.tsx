"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { PostForm, type PostFormValues } from "@/components/PostForm";
import { api, type PostRead } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function EditPostPage() {
  const { accessToken, hasRole } = useAuth();
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [post, setPost] = useState<PostRead | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!accessToken) return;
    api.getManagePost(Number(params.id), accessToken).then(setPost).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to load post."));
  }, [accessToken, params.id]);

  async function submit(values: PostFormValues, publish: boolean) {
    if (!accessToken || !post) return;
    setError("");
    try { await api.updatePost(post.id, { ...values, dek: values.dek || null }, accessToken); if (publish) await api.publishPost(post.id, accessToken); router.push("/admin/posts"); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to update post."); }
  }

  if (error && !post) return <main className="admin-content"><p className="form-error">{error}</p></main>;
  if (!post) return <main className="center-state"><p>Loading post...</p></main>;
  return <main className="admin-content narrow-content"><h1>Refine the story.</h1><p className="muted">{post.status} · Last updated {new Date(post.updated_at).toLocaleString()}</p><PostForm initialValues={{ title: post.title, slug: post.slug, dek: post.dek || "", body: post.body, is_breaking: post.is_breaking, category_ids: post.categories?.map((category) => category.id) ?? [], tag_ids: post.tags?.map((tag) => tag.id) ?? [] }} onSubmit={submit} canPublish={hasRole("admin", "editor")} postId={post.id} submitLabel="Save changes" submittingLabel="Saving..." error={error} /></main>;
}
