"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type CommentAuditRead, type CommentStatus, type ModerationCommentRead, type ReportedCommentRead } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function CommentsPage() {
  const { accessToken } = useAuth();
  const [comments, setComments] = useState<ModerationCommentRead[]>([]);
  const [reports, setReports] = useState<ReportedCommentRead[]>([]);
  const [history, setHistory] = useState<CommentAuditRead[]>([]);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    if (!accessToken) return;
    try {
      const [queue, reported, audits] = await Promise.all([api.getPendingComments(accessToken), api.getReportedComments(accessToken), api.getModerationHistory(accessToken)]);
      setComments(queue); setReports(reported); setHistory(audits);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load comments."); }
  }, [accessToken]);
  useEffect(() => { const timer = window.setTimeout(() => { void load(); }, 0); return () => window.clearTimeout(timer); }, [load]);
  async function moderate(commentId: number, status: CommentStatus) {
    if (!accessToken) return;
    try { await api.moderateComment(commentId, status, accessToken); await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to moderate comment."); }
  }
  return <main className="admin-content"><div className="admin-heading"><div><p className="eyebrow">Community</p><h1>Moderation queue.</h1><p className="muted">Verified comments, automated flags, and public reports.</p></div><span className="section-count">{comments.length.toString().padStart(2, "0")} pending</span></div>{error && <p className="form-error">{error}</p>}<div className="moderation-list">{comments.map((comment) => <article className="moderation-item" key={comment.id}><div><p className="comment-author">{comment.author_name} {comment.status === "flagged" && <span className="eyebrow">Flagged</span>}</p><time>{new Date(comment.created_at).toLocaleString()}</time></div><p>{comment.body}</p>{comment.spam_reason && <small className="muted">Spam check: {comment.spam_reason}</small>}<div className="moderation-actions"><button className="button button-dark" onClick={() => moderate(comment.id, "approved")}>Approve</button><button className="button button-outline" onClick={() => moderate(comment.id, "spam")}>Mark spam</button><button className="text-button danger" onClick={() => moderate(comment.id, "rejected")}>Reject</button></div></article>)}{!comments.length && !error && <div className="empty-state"><h2>Queue clear.</h2><p>There are no verified comments awaiting review.</p></div>}</div>{reports.length > 0 && <section className="moderation-list"><p className="eyebrow">Public reports</p><h2>Reported comments</h2>{reports.map((comment) => <article className="moderation-item" key={comment.id}><p className="comment-author">{comment.author_name}</p><p>{comment.body}</p><small className="muted">{comment.reports.map((report) => report.reason).join(" · ")}</small><div className="moderation-actions"><button className="button button-outline" onClick={() => moderate(comment.id, "flagged")}>Flag for review</button><button className="text-button danger" onClick={() => moderate(comment.id, "rejected")}>Reject</button></div></article>)}</section>}<section className="moderation-list"><p className="eyebrow">Audit trail</p><h2>Recent moderation actions</h2>{history.map((audit) => <article className="moderation-item" key={audit.id}><p className="comment-author">Comment #{audit.comment_id}: {audit.action}</p><time>Editor #{audit.actor_id} · {new Date(audit.created_at).toLocaleString()}</time></article>)}{!history.length && <p className="muted">No moderation actions recorded yet.</p>}</section></main>;
}
