"use client";

import { useRef, useState, type ChangeEvent, type FormEvent } from "react";
import { api } from "@/lib/api";
import { MarkdownContent } from "@/components/MarkdownContent";
import { useAuth } from "@/lib/auth/AuthProvider";

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
  onSubmit: (values: PostFormValues, publish: boolean) => Promise<void>;
  canPublish: boolean;
  postId?: number;
  error?: string;
  success?: string;
}

export function PostForm({ initialValues, submitLabel, submittingLabel, onSubmit, canPublish, postId, error, success }: PostFormProps) {
  const { accessToken } = useAuth();
  const [form, setForm] = useState<PostFormValues>({ title: "", slug: "", dek: "", body: "", is_breaking: false, ...initialValues });
  const [submitting, setSubmitting] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  function update(field: keyof PostFormValues, value: string | boolean) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function replaceSelection(replacement: string, selectionStart: number, selectionEnd: number) {
    const textarea = textareaRef.current;
    if (!textarea) return;
    const body = form.body.slice(0, selectionStart) + replacement + form.body.slice(selectionEnd);
    update("body", body);
    requestAnimationFrame(() => {
      textarea.focus();
      textarea.setSelectionRange(selectionStart, selectionStart + replacement.length);
    });
  }

  function wrapSelection(prefix: string, suffix = prefix, fallback = "text") {
    const textarea = textareaRef.current;
    if (!textarea) return;
    const { selectionStart, selectionEnd } = textarea;
    const selected = form.body.slice(selectionStart, selectionEnd) || fallback;
    replaceSelection(`${prefix}${selected}${suffix}`, selectionStart, selectionEnd);
  }

  function prefixLines(prefix: string, fallback = "List item") {
    const textarea = textareaRef.current;
    if (!textarea) return;
    const { selectionStart, selectionEnd } = textarea;
    const selected = form.body.slice(selectionStart, selectionEnd) || fallback;
    replaceSelection(selected.split("\n").map((line) => `${prefix}${line}`).join("\n"), selectionStart, selectionEnd);
  }

  function insertLink() {
    const url = window.prompt("Link URL:");
    if (url) wrapSelection("[", `](${url})`, "link text");
  }

  function insertTable() {
    replaceSelection("| Column 1 | Column 2 |\n| --- | --- |\n| Cell | Cell |", textareaRef.current?.selectionStart ?? form.body.length, textareaRef.current?.selectionEnd ?? form.body.length);
  }

  async function uploadImage(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    const altText = window.prompt("Describe this image for readers:");
    if (!altText) return;
    setUploadError("");
    setUploading(true);
    try {
      if (!accessToken) throw new Error("Your session has expired. Please sign in again.");
      const upload = await api.requestUpload({ filename: file.name, content_type: file.type, alt_text: altText, post_id: postId }, accessToken);
      const response = await fetch(upload.upload_url, { method: "PUT", headers: { "Content-Type": file.type }, body: file });
      if (!response.ok) throw new Error("The image upload was rejected by storage.");
      const textarea = textareaRef.current;
      const selectionStart = textarea?.selectionStart ?? form.body.length;
      const selectionEnd = textarea?.selectionEnd ?? selectionStart;
      replaceSelection(`![${altText}](${upload.media_url})`, selectionStart, selectionEnd);
    } catch (reason) {
      setUploadError(reason instanceof Error ? reason.message : "Unable to upload image.");
    } finally {
      setUploading(false);
    }
  }

  async function submit(publish: boolean) {
    setSubmitting(true);
    try {
      await onSubmit({ ...form }, publish);
    } finally {
      setSubmitting(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submit(false);
  }

  return <form className="editor-form" onSubmit={handleSubmit}>
    <label>Headline<input value={form.title} onChange={(event) => update("title", event.target.value)} required /></label>
    <label>Slug<input value={form.slug} onChange={(event) => update("slug", event.target.value)} required /></label>
    <label>Dek <span className="field-note">Optional</span><input value={form.dek} onChange={(event) => update("dek", event.target.value)} /></label>
    <div className="body-field"><div className="body-label"><span>Body <span className="field-note">Markdown accepted</span></span><button className="text-button" type="button" onClick={() => setPreviewOpen((current) => !current)}>{previewOpen ? "Hide preview" : "Show preview"}</button></div><div className={previewOpen ? "editor-workspace editor-workspace-split" : "editor-workspace"}><div><div className="markdown-toolbar" aria-label="Markdown formatting"><button type="button" onClick={() => wrapSelection("**", "**", "bold text")} title="Bold">Bold</button><button type="button" onClick={() => wrapSelection("*", "*", "italic text")} title="Italic">Italic</button><button type="button" onClick={insertLink} title="Link">Link</button><button type="button" onClick={() => wrapSelection("`", "`", "code")} title="Inline code">Inline code</button><button type="button" onClick={() => wrapSelection("```\n", "\n```", "code block")} title="Code block">Code block</button><button type="button" onClick={() => prefixLines("## ", "Heading")} title="Heading">Heading</button><button type="button" onClick={() => prefixLines("- ", "List item")} title="Bulleted list">Bulleted list</button><button type="button" onClick={() => prefixLines("1. ", "List item")} title="Numbered list">Numbered list</button><button type="button" onClick={insertTable} title="Table">Table</button><button type="button" onClick={() => prefixLines("> ", "Quote")} title="Blockquote">Blockquote</button><button type="button" onClick={() => imageInputRef.current?.click()} disabled={uploading} title="Insert image">{uploading ? "Uploading..." : "Insert image"}</button><input ref={imageInputRef} className="visually-hidden" type="file" accept="image/*" onChange={uploadImage} /></div><textarea ref={textareaRef} className="body-editor" value={form.body} onChange={(event) => update("body", event.target.value)} required /></div>{previewOpen && <div className="markdown-preview"><p className="preview-label">Live preview</p><MarkdownContent source={form.body || "_Your story preview will appear here._"} className="article-body" /></div>}</div></div>
    <label className="check-label"><input type="checkbox" checked={form.is_breaking} onChange={(event) => update("is_breaking", event.target.checked)} /> Mark as breaking news</label>
    {(error || uploadError) && <p className="form-error">{error || uploadError}</p>}
    {success && <p className="form-success">{success}</p>}
    <div className="editor-actions"><button type="submit" className="button button-outline" disabled={submitting || uploading}>{submitting ? submittingLabel : submitLabel}</button>{canPublish && <button type="button" className="button button-dark" disabled={submitting || uploading} onClick={() => void submit(true)}>{submitting ? "Publishing..." : "Publish"}</button>}</div>
  </form>;
}
