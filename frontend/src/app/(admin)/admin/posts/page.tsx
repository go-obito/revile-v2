"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, type PostRead, type PostStatus } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

const filters: { label: string; value?: PostStatus }[] = [
  { label: "All" },
  { label: "Draft", value: "draft" },
  { label: "Scheduled", value: "scheduled" },
  { label: "Published", value: "published" },
  { label: "Archived", value: "archived" },
];

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export default function PostsPage() {
  const { accessToken, hasRole } = useAuth();
  const searchParams = useSearchParams();
  const status = searchParams.get("status") as PostStatus | null;
  const [posts, setPosts] = useState<PostRead[]>([]);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);
  const canPublish = hasRole("admin", "editor");

  useEffect(() => {
    if (!accessToken) return;
    let cancelled = false;
    api.getManagePosts({ status: status ?? undefined }, accessToken).then((result) => {
      if (!cancelled) { setError(""); setPosts(result.items); }
    }).catch((reason) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : "Unable to load posts.");
    });
    return () => { cancelled = true; };
  }, [accessToken, status]);

  async function updatePost(postId: number, action: () => Promise<PostRead>) {
    setBusyId(postId);
    try { const updated = await action(); setPosts((current) => current.map((post) => post.id === updated.id ? updated : post).filter((post) => !status || post.status === status)); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to update post."); } finally { setBusyId(null); }
  }

  function schedule(postId: number) {
    const value = window.prompt("Schedule for (ISO date and time with timezone):", new Date(Date.now() + 86400000).toISOString());
    if (value && accessToken) updatePost(postId, () => api.schedulePost(postId, value, accessToken));
  }

  return <main className="admin-content"><div className="admin-heading"><div><h1>Post desk.</h1><p className="muted">Track every dispatch from draft to publication.</p></div><Link className="button button-dark" href="/admin/posts/new">Write a post</Link></div><nav className="post-filters" aria-label="Filter posts">{filters.map((filter) => <Link className={!status && !filter.value || status === filter.value ? "active" : ""} href={filter.value ? `/admin/posts?status=${filter.value}` : "/admin/posts"} key={filter.label}>{filter.label}</Link>)}</nav>{error && <p className="form-error">{error}</p>}<div className="post-list">{posts.map((post) => <article className="post-row" key={post.id}><div className="post-row-main"><div><span className={`post-status status-${post.status}`}>{post.status}</span>{post.is_breaking && <span className="post-breaking">Breaking</span>}</div><h2><Link href={`/admin/posts/${post.id}/edit`}>{post.title}</Link></h2><p className="muted">{post.author_name || `Author #${post.author_id}`} · Updated {formatDate(post.updated_at)}</p></div><div className="post-row-actions"><Link className="button button-outline" href={`/admin/posts/${post.id}/edit`}>Edit</Link>{canPublish && post.status !== "published" && <button className="button button-dark" disabled={busyId === post.id} onClick={() => accessToken && updatePost(post.id, () => api.publishPost(post.id, accessToken))}>Publish</button>}{canPublish && post.status === "published" && <button className="button button-outline" disabled={busyId === post.id} onClick={() => accessToken && updatePost(post.id, () => api.unpublishPost(post.id, accessToken))}>Unpublish</button>}{canPublish && post.status !== "published" && <button className="button button-outline" disabled={busyId === post.id} onClick={() => schedule(post.id)}>Schedule</button>}{canPublish && !post.is_breaking && <button className="text-button" disabled={busyId === post.id} onClick={() => accessToken && updatePost(post.id, () => api.flagBreaking(post.id, accessToken))}>Flag breaking</button>}</div></article>)}{!posts.length && !error && <div className="empty-state"><h2>No posts here.</h2><p>There are no posts matching this status filter.</p></div>}</div></main>;
}
