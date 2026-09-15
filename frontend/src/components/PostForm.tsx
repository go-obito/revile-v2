"use client";

import { FormEvent, useState } from "react";

export interface PostFormValues {
  title: string;
  slug: string;
  dek: string;
  body: string;
  is_breaking: boolean;
}

interface PostFormProps {
  initialValues?: Partial<PostFormValues>;
  submitLabel: string;
  submittingLabel: string;
  onSubmit: (values: PostFormValues) => Promise<void>;
  error?: string;
  success?: string;
}

export function PostForm({ initialValues, submitLabel, submittingLabel, onSubmit, error, success }: PostFormProps) {
  const [form, setForm] = useState<PostFormValues>({ title: "", slug: "", dek: "", body: "", is_breaking: false, ...initialValues });
  const [submitting, setSubmitting] = useState(false);

  function update(field: keyof PostFormValues, value: string | boolean) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({ ...form });
    } finally {
      setSubmitting(false);
    }
  }

  return <form className="editor-form" onSubmit={submit}>
    <label>Headline<input value={form.title} onChange={(event) => update("title", event.target.value)} required /></label>
    <label>Slug<input value={form.slug} onChange={(event) => update("slug", event.target.value)} required /></label>
    <label>Dek <span className="field-note">Optional</span><input value={form.dek} onChange={(event) => update("dek", event.target.value)} /></label>
    <label>Body <span className="field-note">Markdown accepted</span><textarea className="body-editor" value={form.body} onChange={(event) => update("body", event.target.value)} required /></label>
    <label className="check-label"><input type="checkbox" checked={form.is_breaking} onChange={(event) => update("is_breaking", event.target.checked)} /> Mark as breaking news</label>
    {error && <p className="form-error">{error}</p>}
    {success && <p className="form-success">{success}</p>}
    <button className="button button-dark" disabled={submitting}>{submitting ? submittingLabel : submitLabel}</button>
  </form>;
}
