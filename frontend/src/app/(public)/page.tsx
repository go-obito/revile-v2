/* eslint-disable @next/next/no-img-element -- Featured CMS images can originate from a configured image host or legacy story markdown. */
import Link from "next/link";
import { api } from "@/lib/api";
import { NewsletterForm } from "@/components/NewsletterForm";
import { PostCard } from "@/components/PostCard";

async function getHomeData() {
  const [breaking, posts, categories] = await Promise.allSettled([api.getBreakingPosts(), api.getPosts({ limit: 12 }), api.getCategories()]);
  return { breaking: breaking.status === "fulfilled" ? breaking.value : [], posts: posts.status === "fulfilled" ? posts.value.items : [], categories: categories.status === "fulfilled" ? categories.value : [] };
}

export default async function HomePage() {
  const { breaking, posts } = await getHomeData();
  const lead = posts[0];
  const supportingPosts = posts.slice(1, 3);
  const rankedPosts = posts.slice(3, 6);
  const topicPosts = posts.slice(6);
  const topicColumns = [topicPosts.slice(0, Math.ceil(topicPosts.length / 2)), topicPosts.slice(Math.ceil(topicPosts.length / 2))];
  return <main>
    <section className="shell lead-section">
      {lead ? <div className="lead-layout"><div className="lead-story"><div className="lead-copy">{(lead.categories?.[0]?.name || (lead.is_breaking ? "Breaking news" : "")) && <p className="lead-category">{lead.categories?.[0]?.name || "Breaking news"}</p>}<h1><Link href={`/posts/${lead.slug}`}>{lead.title}</Link></h1>{lead.dek && <p className="lead-dek">{lead.dek}</p>}<div className="lead-footer"><span>By {lead.author_name ?? "Revile newsroom"}</span><Link className="arrow-link" href={`/posts/${lead.slug}`}>Read the story <span>→</span></Link></div></div>{lead.featured_image_url ? <Link href={`/posts/${lead.slug}`} className="lead-image"><img src={lead.featured_image_url} alt={lead.featured_image_alt} /></Link> : <div className="lead-art" aria-hidden="true"><span>R</span></div>}</div>{supportingPosts.length > 0 && <aside className="lead-rail"><div className="lead-rail-heading"><span>Also reading</span><span>{supportingPosts.length} stories</span></div>{supportingPosts.map((post) => <PostCard key={post.id} post={post} compact />)}</aside>}</div> : <div className="empty-state"><h1>The desk is quiet.</h1><p>No published stories are available yet.</p></div>}
    </section>
    {breaking.length > 0 && <section className="breaking-section"><div className="shell"><h2 className="section-title">Breaking now</h2><div className="breaking-grid">{breaking.slice(0, 3).map((post) => <PostCard key={post.id} post={post} compact />)}</div></div></section>}
    {rankedPosts.length > 0 && <section className="shell ranked-section"><div className="section-heading"><h2>Most read</h2><span className="section-count">The conversation</span></div><div className="ranked-grid">{rankedPosts.map((post, index) => <Link className="ranked-item" href={`/posts/${post.slug}`} key={post.id}><span className="rank">{String(index + 1).padStart(2, "0")}</span><span>{post.title}</span></Link>)}</div></section>}
    {topicPosts.length > 0 && <section className="shell topic-section"><div className="topic-grid">{topicColumns.map((column, index) => <section className="topic-column" key={index}><div className="topic-heading"><h2>{index === 0 ? "Latest reporting" : "In focus"}</h2><Link href={column[0]?.categories?.[0] ? `/categories/${column[0].categories[0].slug}` : "/search"}>See full section <span>→</span></Link></div>{column.map((post) => <PostCard key={post.id} post={post} compact />)}</section>)}</div></section>}
    <section className="shell newsletter-panel"><div><h2>One considered read. Every week.</h2><p>Original reporting and sharp analysis, sent when there’s something worth your attention.</p></div><NewsletterForm /></section>
  </main>;
}
