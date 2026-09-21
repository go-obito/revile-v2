import type { CSSProperties } from "react";

import type { CommentRead } from "@/lib/api";

interface CommentNode extends CommentRead {
  replies: CommentNode[];
}

function buildThread(comments: CommentRead[]) {
  const nodes = new Map<number, CommentNode>();
  const roots: CommentNode[] = [];

  for (const comment of comments) nodes.set(comment.id, { ...comment, replies: [] });
  for (const comment of nodes.values()) {
    const parent = comment.parent_id ? nodes.get(comment.parent_id) : undefined;
    if (parent && parent.id !== comment.id) parent.replies.push(comment);
    else roots.push(comment);
  }
  return roots;
}

function CommentItem({ comment, depth = 0 }: { comment: CommentNode; depth?: number }) {
  const submitted = new Date(comment.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
  const indentation = { "--comment-depth": Math.min(depth, 3) } as CSSProperties;

  return <article className="public-comment" style={indentation}>
    <header><strong>{comment.author_name}</strong><time dateTime={comment.created_at}>{submitted}</time></header>
    <p>{comment.body}</p>
    {comment.replies.length > 0 && <div className="comment-replies">{comment.replies.map((reply) => <CommentItem key={reply.id} comment={reply} depth={depth + 1} />)}</div>}
  </article>;
}

export function CommentThread({ comments }: { comments: CommentRead[] }) {
  const roots = buildThread(comments);
  if (roots.length === 0) return <p className="comments-empty">No comments yet - be the first to comment.</p>;
  return <div className="comment-thread" aria-label="Approved comments">{roots.map((comment) => <CommentItem key={comment.id} comment={comment} />)}</div>;
}
