/* eslint-disable @next/next/no-img-element -- Article media accepts existing CMS and legacy markdown image URLs. */
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CommentForm } from "@/components/CommentForm";
import { CommentThread } from "@/components/CommentThread";
import { MarkdownContent } from "@/components/MarkdownContent";
import { ArticleActions } from "@/components/ArticleActions";
import { NewsletterForm } from "@/components/NewsletterForm";
import { api } from "@/lib/api";

function removeFeaturedImage(source: string, imageUrl: string | null) {
  if (!imageUrl) return source;
  const escapedUrl = imageUrl.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return source
    .replace(new RegExp(`!\\[[^\\]]*\\]\\(${escapedUrl}(?:\\s+[^)]*)?\\)\\s*`, "g"), "")
    .replace(new RegExp(`<img\\b(?=[^>]*\\bsrc=["']${escapedUrl}["'])[^>]*>\\s*`, "gi"), "");
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const post = await api.getPost(slug).catch(() => null);
  return post ? { title: post.title, description: post.dek ?? undefined, openGraph: post.featured_image_url ? { images: [{ url: post.featured_image_url, alt: post.featured_image_alt }] } : undefined } : { title: "Story not found" };
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await api.getPost(slug).catch(() => null);
  if (!post) notFound();
  const comments = await api.getApprovedComments(post.id).catch(() => []);
  const publishedAt = post.published_at ?? post.created_at;
  const readingMinutes = Math.max(1, Math.ceil(post.body.replace(/[#*_>`~\-()[\]]/g, " ").trim().split(/\s+/).filter(Boolean).length / 220));
  const category = post.categories?.[0];
  const articleBody = removeFeaturedImage(post.body, post.featured_image_url);
  return <main className="article-page">
    <article className="article-shell">
      <div className="article-meta"><Link href={category ? `/categories/${category.slug}` : "/"}>{category?.name ?? (post.is_breaking ? "Breaking" : "Dispatch")}</Link><time dateTime={publishedAt}>{new Date(publishedAt).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</time><span>{readingMinutes} min read</span></div>
      <h1>{post.title}</h1>
      {post.dek && <p className="article-dek">{post.dek}</p>}
      <div className="article-byline"><span>By <strong>{post.author_name ?? "Revile newsroom"}</strong></span><span>Updated {new Date(post.updated_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</span><ArticleActions title={post.title} /></div>
      {post.featured_image_url && <figure className="article-hero"><img src={post.featured_image_url} alt={post.featured_image_alt} /><figcaption>{post.featured_image_alt}</figcaption></figure>}
      <MarkdownContent source={articleBody} className="article-body" />
      <aside className="article-newsletter"><h2>Get the next essential read.</h2><NewsletterForm compact /></aside>
    </article>
    <section className="comments-shell"><h2>Comments</h2><CommentThread comments={comments} postId={post.id} /><div className="comment-compose"><h3>Join the record.</h3><p className="muted">Comments are reviewed before appearing publicly.</p><CommentForm postId={post.id} /></div></section>
  </main>;
}
