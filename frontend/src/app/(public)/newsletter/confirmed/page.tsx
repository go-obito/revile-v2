import Link from "next/link";

export default async function NewsletterConfirmedPage({ searchParams }: { searchParams: Promise<{ state?: string }> }) {
  const { state } = await searchParams;
  const content = state === "confirmed" ? ["You’re on the list.", "Your Revile briefing subscription is confirmed."] : state === "retry" ? ["Almost there.", "We could not complete your confirmation. Please try the link again shortly."] : ["That link has expired.", "Request a fresh confirmation email from the homepage."];
  return <main className="center-state newsletter-result"><p className="eyebrow">The Revile briefing</p><h1>{content[0]}</h1><p className="muted">{content[1]}</p><Link className="button button-dark" href="/">Return to the latest</Link></main>;
}
