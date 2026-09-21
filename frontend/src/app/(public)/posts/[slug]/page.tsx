import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { CommentForm } from "@/components/CommentForm";
import { CommentThread } from "@/components/CommentThread";
import { MarkdownContent } from "@/components/MarkdownContent";
import { api } from "@/lib/api";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const post = await api.getPost(slug).catch(() => null);
  return post ? { title: post.title, description: post.dek ?? undefined } : { title: "Story not found" };
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await api.getPost(slug).catch(() => null);
  if (!post) notFound();
  const comments = await api.getApprovedComments(post.id);
  const publishedAt = post.published_at ?? post.created_at;

  return <main className="article-page">
    <article className="article-shell">
      <div className="article-meta"><span>{post.is_breaking ? "Breaking" : "Dispatch"}</span><time dateTime={publishedAt}>{new Date(publishedAt).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</time></div>
      <h1>{post.title}</h1>
      {post.dek && <p className="article-dek">{post.dek}</p>}
      <div className="article-byline">By Revile newsroom <span>&middot;</span> Updated {new Date(post.updated_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</div>
      <MarkdownContent source={post.body} className="article-body" />
    </article>
    <section className="comments-shell">
      <p className="eyebrow">Community record</p>
      <h2>Comments</h2>
      <CommentThread comments={comments} postId={post.id} />
      <div className="comment-compose">
        <p className="eyebrow">Have a view?</p>
        <h3>Join the record.</h3>
        <p className="muted">Comments are reviewed before appearing publicly.</p>
        <CommentForm postId={post.id} />
      </div>
    </section>
  </main>;
}
