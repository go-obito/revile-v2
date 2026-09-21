/* eslint-disable @next/next/no-img-element -- Story images are CMS URLs from markdown and may use multiple trusted hosts. */
import Link from "next/link";
import type { PostRead } from "@/lib/api";

export function PostCard({ post, compact = false, index }: { post: PostRead; compact?: boolean; index?: number }) {
  const section = post.categories[0]?.name ?? (post.is_breaking ? "Breaking" : "Analysis");
  return (
    <article className={compact ? "post-card post-card-compact" : "post-card"}>
      {post.featured_image_url ? <Link className="post-card-image" href={`/posts/${post.slug}`} aria-label={`Read ${post.title}`}><img src={post.featured_image_url} alt={post.featured_image_alt} loading="lazy" /></Link> : <div className="post-card-placeholder" aria-hidden="true"><span /></div>}
      <div className="post-card-content">
        <div className="post-card-meta">{index !== undefined && <span className="post-card-index">{index.toString().padStart(2, "0")}</span>}<span>{section}</span><time dateTime={post.published_at ?? post.created_at}>{new Date(post.published_at ?? post.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</time></div>
        <h3><Link href={`/posts/${post.slug}`}>{post.title}</Link></h3>
        {post.dek && <p>{post.dek}</p>}
      </div>
    </article>
  );
}
