import { redirect } from "next/navigation";

export default async function NewsletterConfirmRelay({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const { token } = await searchParams;
  redirect(`/api/v1/newsletter/confirm?token=${encodeURIComponent(token ?? "")}`);
}
