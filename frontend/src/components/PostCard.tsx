import Link from "next/link";
import type { PostRead } from "@/lib/api";

export function PostCard({ post, compact = false, index }: { post: PostRead; compact?: boolean; index?: number }) {
  return (
    <article className={compact ? "post-card post-card-compact" : "post-card"}>
      <div className="post-card-meta">{index !== undefined && <span className="post-card-index">{index.toString().padStart(2, "0")}</span>}<span>{post.is_breaking ? "Breaking" : "Dispatch"}</span><time dateTime={post.published_at ?? post.created_at}>{new Date(post.published_at ?? post.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</time></div>
      <h3><Link href={`/posts/${post.slug}`}>{post.title}</Link></h3>
      {post.dek && <p>{post.dek}</p>}
    </article>
  );
}
