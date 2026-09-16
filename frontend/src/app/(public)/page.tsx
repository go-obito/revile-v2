import Link from "next/link";
import { api, type CategoryRead } from "@/lib/api";
import { PostCard } from "@/components/PostCard";

async function getHomeData() {
  const [breaking, posts, categories] = await Promise.allSettled([api.getBreakingPosts(), api.getPosts({ limit: 12 }), api.getCategories()]);
  return {
    breaking: breaking.status === "fulfilled" ? breaking.value : [],
    posts: posts.status === "fulfilled" ? posts.value.items : [],
    categories: categories.status === "fulfilled" ? categories.value : [],
  };
}

export default async function HomePage() {
  const { breaking, posts, categories } = await getHomeData();
  const lead = posts[0];
  const latestPosts = posts.slice(1);
  return <main><section className="shell lead-section"><div className="section-kicker"><span>01</span><span>THE DAILY DISPATCH</span><span>Independent technology reporting</span></div>{lead ? <div className="lead-story"><div><p className="eyebrow">{lead.is_breaking ? "Breaking news" : "Lead story"}</p><h1><Link href={`/posts/${lead.slug}`}>{lead.title}</Link></h1>{lead.dek && <p className="lead-dek">{lead.dek}</p>}<Link className="arrow-link" href={`/posts/${lead.slug}`}>Read the dispatch <span>↗</span></Link></div><div className="lead-index"><span>LEAD</span><strong>{(posts.findIndex((post) => post.id === lead.id) + 1).toString().padStart(2, "0")}</strong></div></div> : <div className="empty-state"><h1>The desk is quiet.</h1><p>No published stories are available yet.</p></div>}</section>{breaking.length > 0 && <section className="breaking-section"><div className="shell"><div className="section-kicker"><span>LIVE</span><span>BREAKING NOW</span></div><div className="breaking-grid">{breaking.slice(0, 3).map((post, index) => <PostCard key={post.id} post={post} compact index={index + 1} />)}</div></div></section>}<section className="shell latest-section"><div className="section-heading"><div><p className="eyebrow">The latest</p><h2>What matters now.</h2></div><span className="section-count">{posts.length.toString().padStart(2, "0")} reports</span></div><div className="news-grid">{latestPosts.map((post, index) => <PostCard key={post.id} post={post} index={index + 2} />)}</div></section><section className="shell category-strip"><div className="section-kicker"><span>INDEX</span><span>BY BEAT</span></div><div className="category-links">{categories.map((category: CategoryRead) => <Link key={category.id} href={`/categories/${category.slug}`}>{category.name}<span>↗</span></Link>)}</div></section></main>;
}
