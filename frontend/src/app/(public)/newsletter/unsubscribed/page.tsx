import Link from "next/link";

export default async function NewsletterUnsubscribedPage({ searchParams }: { searchParams: Promise<{ state?: string }> }) {
  const { state } = await searchParams;
  const content = state === "confirmed" ? ["You’ve been unsubscribed.", "You will no longer receive the Revile briefing."] : state === "retry" ? ["We could not finish that request.", "Please try the unsubscribe link again shortly."] : ["That link is no longer active.", "Your subscription may already have been updated."];
  return <main className="center-state newsletter-result"><h1>{content[0]}</h1><p className="muted">{content[1]}</p><Link className="button button-dark" href="/">Return to the latest</Link></main>;
}
