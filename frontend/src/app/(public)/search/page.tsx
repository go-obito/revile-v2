import Link from "next/link";
import { api } from "@/lib/api";
import { PostCard } from "@/components/PostCard";

export default async function SearchPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q = "" } = await searchParams;
  const results = q.length >= 2 ? await api.searchPosts(q).catch(() => []) : [];
  return <main className="shell search-page"><div className="archive-heading"><p className="eyebrow">Search the reporting</p><h1>Find the signal.</h1><form className="search-form"><input name="q" defaultValue={q} placeholder="Search headlines and reporting" aria-label="Search headlines and reporting" /><button className="button button-dark">Search</button></form></div>{q && <p className="result-label">{results.length} result{results.length === 1 ? "" : "s"} for “{q}”</p>}<div className="archive-list">{results.map((post) => <PostCard key={post.id} post={post} />)}{q && !results.length && <div className="empty-state"><h2>No matching dispatches.</h2><Link className="arrow-link" href="/">Return to the latest</Link></div>}</div></main>;
}
