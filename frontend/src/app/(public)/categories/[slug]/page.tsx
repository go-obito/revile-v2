import type { Metadata } from "next";
import { api } from "@/lib/api";
import { PostCard } from "@/components/PostCard";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  return { title: slug.replaceAll("-", " ") };
}

export default async function CategoryPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const posts = await api.getCategoryPosts(slug).catch(() => ({ items: [], next_cursor: null }));
  const label = slug.replaceAll("-", " ");
  return <main className="shell archive-page"><div className="archive-heading"><p className="eyebrow">Beat archive</p><h1>{label}</h1><p className="muted">The latest reporting filed under this desk.</p></div><div className="archive-list">{posts.items.length ? posts.items.map((post) => <PostCard key={post.id} post={post} />) : <div className="empty-state"><h2>No reports filed here yet.</h2><p>Try another section or return to the latest dispatches.</p></div>}</div></main>;
}
