"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function NewPostPage() {
  const { accessToken } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ title: "", slug: "", dek: "", body: "", is_breaking: false });
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!accessToken) return;
    setError("");
    try { await api.createPost(form, accessToken); setSaved(true); setTimeout(() => router.push("/admin"), 800); } catch (submitError) { setError(submitError instanceof Error ? submitError.message : "Unable to save post."); }
  }
  function update(field: keyof typeof form, value: string | boolean) { setForm((current) => ({ ...current, [field]: value })); }
  return <main className="admin-content narrow-content"><p className="eyebrow">New dispatch</p><h1>Write the story.</h1><form className="editor-form" onSubmit={submit}><label>Headline<input value={form.title} onChange={(event) => update("title", event.target.value)} required /></label><label>Slug<input value={form.slug} onChange={(event) => update("slug", event.target.value)} placeholder="headline-in-lowercase" required /></label><label>Dek <span className="field-note">Optional</span><input value={form.dek} onChange={(event) => update("dek", event.target.value)} /></label><label>Body <span className="field-note">Markdown accepted</span><textarea className="body-editor" value={form.body} onChange={(event) => update("body", event.target.value)} required /></label><label className="check-label"><input type="checkbox" checked={form.is_breaking} onChange={(event) => update("is_breaking", event.target.checked)} /> Mark as breaking news</label>{error && <p className="form-error">{error}</p>}{saved && <p className="form-success">Saved. Redirecting to the desk...</p>}<button className="button button-dark" disabled={saved}>{saved ? "Saved" : "Save draft"}</button></form></main>;
}
