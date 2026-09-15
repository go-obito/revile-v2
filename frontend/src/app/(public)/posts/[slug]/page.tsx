import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { CommentForm } from "@/components/CommentForm";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const post = await api.getPost(slug).catch(() => null);
  return post ? { title: post.title, description: post.dek ?? undefined } : { title: "Story not found" };
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await api.getPost(slug).catch(() => null);
  if (!post) notFound();
  return <main className="article-page"><article className="article-shell"><div className="article-meta"><span>{post.is_breaking ? "Breaking" : "Dispatch"}</span><time dateTime={post.published_at ?? post.created_at}>{new Date(post.published_at ?? post.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</time></div><h1>{post.title}</h1>{post.dek && <p className="article-dek">{post.dek}</p>}<div className="article-byline">By Revile newsroom <span>·</span> Updated {new Date(post.updated_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</div><div className="article-body">{post.body.split("\n").map((paragraph, index) => paragraph.trim() ? <p key={index}>{paragraph}</p> : null)}</div></article><section className="comments-shell"><p className="eyebrow">Have a view?</p><h2>Join the record.</h2><p className="muted">Comments are reviewed before appearing publicly.</p><CommentForm postId={post.id} /></section></main>;
}
