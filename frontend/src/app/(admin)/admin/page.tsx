"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function AdminHomePage() {
  const { accessToken, user } = useAuth();
  const [stats, setStats] = useState({ posts: 0, pending: 0 });
  useEffect(() => { if (!accessToken) return; Promise.all([api.getManagePosts({ limit: 100 }, accessToken), api.getPendingCommentCount(accessToken)]).then(([posts, comments]) => setStats({ posts: posts.items.length, pending: comments.count })).catch(() => undefined); }, [accessToken]);
  return <main className="admin-content"><div className="admin-heading"><div><p className="eyebrow">Editorial command center</p><h1>Good morning{user?.name ? `, ${user.name.split(" ")[0]}` : ""}.</h1><p className="muted">Your publishing and community work, in one calm place.</p></div><Link className="button button-dark" href="/admin/posts/new">Write a post</Link></div><section className="dashboard-grid"><Link className="dashboard-card" href="/admin/posts"><span className="card-kicker">Publishing / {stats.posts.toString().padStart(2, "0")}</span><h2>Manage posts</h2><p>Review drafts, scheduled dispatches, and the live archive.</p></Link><Link className="dashboard-card" href="/admin/posts/new"><span className="card-kicker">Writing</span><h2>Draft a dispatch</h2><p>Write, tag, preview, and prepare the next story for the desk.</p></Link><Link className="dashboard-card" href="/admin/comments"><span className="card-kicker">Community / {stats.pending.toString().padStart(2, "0")}</span><h2>Review comments</h2><p>Clear pending responses and keep the public record useful.</p></Link></section></main>;
}
