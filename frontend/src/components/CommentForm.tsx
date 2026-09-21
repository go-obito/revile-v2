"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, type CommentStatus } from "@/lib/api";

type FormValues = { author_name: string; author_email: string; body: string };
type StoredSubmission = { idempotencyKey: string; status: CommentStatus | "retry"; form: FormValues };

const blankForm: FormValues = { author_name: "", author_email: "", body: "" };

function storageKey(postId: number) {
  return `revile:comment-submission:${postId}`;
}

function newIdempotencyKey() {
  return crypto.randomUUID();
}

export function CommentForm({ postId }: { postId: number }) {
  const [form, setForm] = useState<FormValues>(blankForm);
  const [submission, setSubmission] = useState<StoredSubmission | null>(null);
  const [state, setState] = useState<"loading" | "idle" | "sending" | "error">("loading");

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const stored = window.localStorage.getItem(storageKey(postId));
      if (stored) {
        try {
          const parsed = JSON.parse(stored) as StoredSubmission;
          setSubmission(parsed);
          setForm(parsed.form);
        } catch {
          window.localStorage.removeItem(storageKey(postId));
        }
      }
      setState("idle");
    }, 0);
    return () => window.clearTimeout(timer);
  }, [postId]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const idempotencyKey = submission?.idempotencyKey ?? newIdempotencyKey();
    const pending: StoredSubmission = { idempotencyKey, status: "retry", form };
    setSubmission(pending);
    window.localStorage.setItem(storageKey(postId), JSON.stringify(pending));
    setState("sending");
    try {
      const comment = await api.createComment(postId, { ...form, idempotency_key: idempotencyKey });
      const persisted: StoredSubmission = { ...pending, status: comment.status };
      setSubmission(persisted);
      window.localStorage.setItem(storageKey(postId), JSON.stringify(persisted));
      setForm(blankForm);
      setState("idle");
    } catch {
      setState("error");
    }
  }

  if (state === "loading") return null;
  if (submission?.status === "pending" || submission?.status === "flagged") return <p className="form-success" role="status">Your comment is awaiting moderation.</p>;
  return <form className="comment-form" onSubmit={submit}><div className="form-row"><label>Name<input value={form.author_name} onChange={(event) => setForm({ ...form, author_name: event.target.value })} required /></label><label>Email<input type="email" value={form.author_email} onChange={(event) => setForm({ ...form, author_email: event.target.value })} required /></label></div><label>Comment<textarea value={form.body} onChange={(event) => setForm({ ...form, body: event.target.value })} required minLength={2} /></label>{state === "error" && <p className="form-error">We could not submit that comment. Please try again.</p>}<button className="button button-outline" disabled={state === "sending"}>{state === "sending" ? "Sending..." : "Submit comment"}</button></form>;
}
