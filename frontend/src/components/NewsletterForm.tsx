"use client";

import { FormEvent, useState } from "react";
import { ArrowRight, LoaderCircle } from "lucide-react";
import { api } from "@/lib/api";

export function NewsletterForm({ compact = false }: { compact?: boolean }) {
  const [email, setEmail] = useState("");
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState("sending");
    try {
      await api.subscribeNewsletter(email);
      setState("sent");
      setEmail("");
    } catch {
      setState("error");
    }
  }

  if (state === "sent") return <p className="newsletter-status success" role="status">Check your inbox to confirm your subscription.</p>;
  return <form className={compact ? "newsletter-form newsletter-form-compact" : "newsletter-form"} onSubmit={submit}>
    <label className="visually-hidden" htmlFor={compact ? "footer-email" : "newsletter-email"}>Email address</label>
    <input id={compact ? "footer-email" : "newsletter-email"} type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email address" autoComplete="email" required />
    <button className="newsletter-submit" disabled={state === "sending"}>{state === "sending" ? <LoaderCircle aria-hidden="true" className="spin" /> : <><span>{compact ? "Join" : "Get the briefing"}</span><ArrowRight aria-hidden="true" /></>}</button>
    {state === "error" && <p className="newsletter-status error" role="alert">We couldn’t sign you up. Please try again.</p>}
  </form>;
}
