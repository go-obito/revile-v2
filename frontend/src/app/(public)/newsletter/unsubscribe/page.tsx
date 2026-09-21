import { redirect } from "next/navigation";

export default async function NewsletterUnsubscribeRelay({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const { token } = await searchParams;
  redirect(`/api/v1/newsletter/unsubscribe?token=${encodeURIComponent(token ?? "")}`);
}
