import { LoginForm } from "@/components/LoginForm";

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const { next = "/admin" } = await searchParams;
  return <main className="login-shell"><div className="login-panel"><p className="eyebrow">Editorial desk</p><h1>Sign in to Revile.</h1><p className="muted">Access publishing, moderation, and newsroom tools.</p><LoginForm nextPath={next.startsWith("/") ? next : "/admin"} /></div></main>;
}
