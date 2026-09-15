"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export function CommentForm({ postId }: { postId: number }) {
  const [form, setForm] = useState({ author_name: "", author_email: "", body: "" });
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setState("sending");
    try { await api.createComment(postId, form); setState("sent"); setForm({ author_name: "", author_email: "", body: "" }); } catch { setState("error"); }
  }
  if (state === "sent") return <p className="form-success">Your comment is awaiting editorial approval.</p>;
  return <form className="comment-form" onSubmit={submit}><div className="form-row"><label>Name<input value={form.author_name} onChange={(event) => setForm({ ...form, author_name: event.target.value })} required /></label><label>Email<input type="email" value={form.author_email} onChange={(event) => setForm({ ...form, author_email: event.target.value })} required /></label></div><label>Comment<textarea value={form.body} onChange={(event) => setForm({ ...form, body: event.target.value })} required minLength={2} /></label>{state === "error" && <p className="form-error">We could not submit that comment. Please try again.</p>}<button className="button button-outline" disabled={state === "sending"}>{state === "sending" ? "Sending..." : "Submit comment"}</button></form>;
}
