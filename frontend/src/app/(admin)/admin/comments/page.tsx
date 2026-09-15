"use client";

import { useEffect, useState } from "react";
import { api, type CommentRead, type CommentStatus } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function CommentsPage() {
  const { accessToken } = useAuth();
  const [comments, setComments] = useState<CommentRead[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { if (accessToken) api.getPendingComments(accessToken).then(setComments).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to load comments.")); }, [accessToken]);
  async function moderate(commentId: number, status: CommentStatus) { if (!accessToken) return; try { await api.moderateComment(commentId, status, accessToken); setComments((current) => current.filter((comment) => comment.id !== commentId)); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to moderate comment."); } }
  return <main className="admin-content"><div className="admin-heading"><div><p className="eyebrow">Community</p><h1>Moderation queue.</h1><p className="muted">Pending comments from the public record.</p></div><span className="section-count">{comments.length.toString().padStart(2, "0")} pending</span></div>{error && <p className="form-error">{error}</p>}<div className="moderation-list">{comments.map((comment) => <article className="moderation-item" key={comment.id}><div><p className="comment-author">{comment.author_name}</p><time>{new Date(comment.created_at).toLocaleString()}</time></div><p>{comment.body}</p><div className="moderation-actions"><button className="button button-dark" onClick={() => moderate(comment.id, "approved")}>Approve</button><button className="button button-outline" onClick={() => moderate(comment.id, "spam")}>Mark spam</button><button className="text-button danger" onClick={() => moderate(comment.id, "rejected")}>Reject</button></div></article>)}{!comments.length && !error && <div className="empty-state"><h2>Queue clear.</h2><p>There are no pending comments to review.</p></div>}</div></main>;
}
