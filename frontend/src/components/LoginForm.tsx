"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthProvider";

export function LoginForm({ nextPath }: { nextPath: string }) {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSubmitting(true); setError("");
    try { await login(email, password); router.push(nextPath); } catch (loginError) { setError(loginError instanceof Error ? loginError.message : "Unable to sign in."); } finally { setSubmitting(false); }
  }

  return <form onSubmit={submit} className="stack-form"><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" /></label><label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" /></label>{error && <p className="form-error">{error}</p>}<button className="button button-dark" disabled={submitting}>{submitting ? "Signing in..." : "Sign in"}</button></form>;
}
