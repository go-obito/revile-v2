/* eslint-disable @next/next/no-img-element -- Featured CMS images can originate from a configured image host or legacy story markdown. */
import Link from "next/link";
import { api, type CategoryRead } from "@/lib/api";
import { NewsletterForm } from "@/components/NewsletterForm";
import { PostCard } from "@/components/PostCard";

async function getHomeData() {
  const [breaking, posts, categories] = await Promise.allSettled([api.getBreakingPosts(), api.getPosts({ limit: 12 }), api.getCategories()]);
  return { breaking: breaking.status === "fulfilled" ? breaking.value : [], posts: posts.status === "fulfilled" ? posts.value.items : [], categories: categories.status === "fulfilled" ? categories.value : [] };
}

export default async function HomePage() {
  const { breaking, posts, categories } = await getHomeData();
  const lead = posts[0];
  const latestPosts = posts.slice(1);
  return <main>
    <section className="shell lead-section">
      <div className="section-kicker"><span>Edition 01</span><span>The daily dispatch</span><span>Technology, reported</span></div>
      {lead ? <div className="lead-story"><div className="lead-copy"><p className="eyebrow">{lead.categories[0]?.name ?? (lead.is_breaking ? "Breaking news" : "Lead story")}</p><h1><Link href={`/posts/${lead.slug}`}>{lead.title}</Link></h1>{lead.dek && <p className="lead-dek">{lead.dek}</p>}<div className="lead-footer"><Link className="arrow-link" href={`/posts/${lead.slug}`}>Read the story <span>→</span></Link><span>{lead.author_name ?? "Revile newsroom"}</span></div></div>{lead.featured_image_url ? <Link href={`/posts/${lead.slug}`} className="lead-image"><img src={lead.featured_image_url} alt={lead.featured_image_alt} /></Link> : <div className="lead-art" aria-hidden="true"><span>R</span></div>}</div> : <div className="empty-state"><h1>The desk is quiet.</h1><p>No published stories are available yet.</p></div>}
    </section>
    {breaking.length > 0 && <section className="breaking-section"><div className="shell"><div className="section-kicker"><span>Live</span><span>Breaking now</span></div><div className="breaking-grid">{breaking.slice(0, 3).map((post, index) => <PostCard key={post.id} post={post} compact index={index + 1} />)}</div></div></section>}
    <section className="shell latest-section"><div className="section-heading"><div><p className="eyebrow">The latest</p><h2>What matters now.</h2></div><span className="section-count">{posts.length.toString().padStart(2, "0")} reports</span></div><div className="news-grid">{latestPosts.map((post, index) => <PostCard key={post.id} post={post} index={index + 2} />)}</div></section>
    <section className="shell newsletter-panel"><div><p className="eyebrow">The Revile briefing</p><h2>One considered read. Every week.</h2><p>Original reporting and sharp analysis, sent when there’s something worth your attention.</p></div><NewsletterForm /></section>
    <section className="shell category-strip"><div className="section-kicker"><span>Index</span><span>Explore by beat</span></div><div className="category-links">{categories.map((category: CategoryRead) => <Link key={category.id} href={`/categories/${category.slug}`}>{category.name}<span>→</span></Link>)}</div></section>
  </main>;
}
