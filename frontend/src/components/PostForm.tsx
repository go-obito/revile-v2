"use client";

import { useRef, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";
import { Bold, Code2, ImagePlus, Italic, Link2, List, ListOrdered, Quote, Redo2, RemoveFormatting, Strikethrough, TableProperties, Underline, Undo2 } from "lucide-react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import { Table } from "@tiptap/extension-table";
import TableRow from "@tiptap/extension-table-row";
import TableHeader from "@tiptap/extension-table-header";
import TableCell from "@tiptap/extension-table-cell";
import UnderlineExtension from "@tiptap/extension-underline";
import { Markdown } from "@tiptap/markdown";
import { upload } from "@imagekit/javascript";
import { api } from "@/lib/api";
import { MarkdownContent } from "@/components/MarkdownContent";
import { useAuth } from "@/lib/auth/AuthProvider";

export interface PostFormValues { title: string; slug: string; dek: string; body: string; is_breaking: boolean; }

interface PostFormProps { initialValues?: Partial<PostFormValues>; submitLabel: string; submittingLabel: string; onSubmit: (values: PostFormValues, publish: boolean) => Promise<void>; canPublish: boolean; postId?: number; error?: string; success?: string; }
interface ToolButtonProps { active?: boolean; disabled?: boolean; label: string; onClick: () => void; children: ReactNode; }

function ToolButton({ active = false, disabled = false, label, onClick, children }: ToolButtonProps) {
  return <button type="button" className={active ? "word-tool is-active" : "word-tool"} onClick={onClick} disabled={disabled} aria-label={label} title={label}>{children}</button>;
}

export function PostForm({ initialValues, submitLabel, submittingLabel, onSubmit, canPublish, postId, error, success }: PostFormProps) {
  const { accessToken } = useAuth();
  const [form, setForm] = useState<PostFormValues>({ title: "", slug: "", dek: "", body: "", is_breaking: false, ...initialValues });
  const [submitting, setSubmitting] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState("");
  const imageInputRef = useRef<HTMLInputElement>(null);
  const editor = useEditor({
    immediatelyRender: false,
    content: form.body,
    contentType: "markdown",
    extensions: [StarterKit, UnderlineExtension, Link.configure({ openOnClick: false }), Image.configure({ allowBase64: false }), Table.configure({ resizable: false }), TableRow, TableHeader, TableCell, Markdown],
    onUpdate: ({ editor: currentEditor }) => update("body", currentEditor.storage.markdown.manager.serialize(currentEditor.getJSON())),
  }, [initialValues?.body]);

  function update(field: keyof PostFormValues, value: string | boolean) { setForm((current) => ({ ...current, [field]: value })); }
  function insertLink() { const url = window.prompt("Link URL:"); if (url) editor?.chain().focus().setLink({ href: url }).run(); }
  function insertTable() { editor?.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(); }

  async function uploadImage(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setUploadError(""); setUploading(true); setUploadProgress(0);
    try {
      if (!accessToken) throw new Error("Your session has expired. Please sign in again.");
      const publicKey = process.env.NEXT_PUBLIC_IMAGEKIT_PUBLIC_KEY;
      const urlEndpoint = process.env.NEXT_PUBLIC_IMAGEKIT_URL_ENDPOINT;
      if (!publicKey || !urlEndpoint) throw new Error("ImageKit is not configured in this environment.");
      const auth = await api.getImageKitAuth(accessToken);
      const result = await upload({ file, fileName: file.name, publicKey, token: auth.token, expire: auth.expire, signature: auth.signature, useUniqueFileName: true, onProgress: (progress) => setUploadProgress(Math.round((progress.loaded / progress.total) * 100)) });
      if (!result.url || !result.fileId) throw new Error("ImageKit did not return an image URL.");
      const altText = window.prompt("Describe this image for readers:");
      if (!altText) return;
      await api.createMediaRecord({ file_url: result.url, imagekit_file_id: result.fileId, alt_text: altText, post_id: postId }, accessToken);
      editor?.chain().focus().setImage({ src: result.url, alt: altText, title: altText }).run();
    } catch (reason) { setUploadError(reason instanceof Error ? reason.message : "Unable to upload image."); }
    finally { setUploadProgress(0); setUploading(false); }
  }

  async function submit(publish: boolean) { setSubmitting(true); try { await onSubmit({ ...form }, publish); } finally { setSubmitting(false); } }
  function handleSubmit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); void submit(false); }
  const headingLevel = editor?.isActive("heading") ? String(editor.getAttributes("heading").level) : "paragraph";

  return <form className="editor-form" onSubmit={handleSubmit}>
    <label>Headline<input value={form.title} onChange={(event) => update("title", event.target.value)} required /></label>
    <label>Slug<input value={form.slug} onChange={(event) => update("slug", event.target.value)} required /></label>
    <label>Dek <span className="field-note">Optional</span><input value={form.dek} onChange={(event) => update("dek", event.target.value)} /></label>
    {uploading && <p className="field-note" role="status">Uploading image: {uploadProgress}%</p>}
    <div className="body-field">
      <div className="body-label"><span>Post body</span><button className="text-button" type="button" onClick={() => setPreviewOpen((current) => !current)}>{previewOpen ? "Hide preview" : "Show preview"}</button></div>
      <div className={previewOpen ? "editor-workspace editor-workspace-split" : "editor-workspace"}>
        <div className="word-editor">
          <div className="word-toolbar" role="toolbar" aria-label="Post formatting">
            <div className="word-tool-group"><ToolButton label="Undo" disabled={!editor?.can().undo()} onClick={() => editor?.chain().focus().undo().run()}><Undo2 /></ToolButton><ToolButton label="Redo" disabled={!editor?.can().redo()} onClick={() => editor?.chain().focus().redo().run()}><Redo2 /></ToolButton></div>
            <div className="word-tool-group word-style-group"><select aria-label="Text style" value={headingLevel} onChange={(event) => { const level = event.target.value; if (level === "paragraph") editor?.chain().focus().setParagraph().run(); else editor?.chain().focus().setHeading({ level: Number(level) as 1 | 2 | 3 }).run(); }}><option value="paragraph">Normal</option><option value="1">Title</option><option value="2">Heading 1</option><option value="3">Heading 2</option></select></div>
            <div className="word-tool-group"><ToolButton label="Bold" active={editor?.isActive("bold")} onClick={() => editor?.chain().focus().toggleBold().run()}><Bold /></ToolButton><ToolButton label="Italic" active={editor?.isActive("italic")} onClick={() => editor?.chain().focus().toggleItalic().run()}><Italic /></ToolButton><ToolButton label="Underline" active={editor?.isActive("underline")} onClick={() => editor?.chain().focus().toggleUnderline().run()}><Underline /></ToolButton><ToolButton label="Strikethrough" active={editor?.isActive("strike")} onClick={() => editor?.chain().focus().toggleStrike().run()}><Strikethrough /></ToolButton><ToolButton label="Clear formatting" onClick={() => editor?.chain().focus().unsetAllMarks().clearNodes().run()}><RemoveFormatting /></ToolButton></div>
            <div className="word-tool-group"><ToolButton label="Bullet list" active={editor?.isActive("bulletList")} onClick={() => editor?.chain().focus().toggleBulletList().run()}><List /></ToolButton><ToolButton label="Numbered list" active={editor?.isActive("orderedList")} onClick={() => editor?.chain().focus().toggleOrderedList().run()}><ListOrdered /></ToolButton><ToolButton label="Quote" active={editor?.isActive("blockquote")} onClick={() => editor?.chain().focus().toggleBlockquote().run()}><Quote /></ToolButton><ToolButton label="Code block" active={editor?.isActive("codeBlock")} onClick={() => editor?.chain().focus().toggleCodeBlock().run()}><Code2 /></ToolButton></div>
            <div className="word-tool-group"><ToolButton label="Insert link" active={editor?.isActive("link")} onClick={insertLink}><Link2 /></ToolButton><ToolButton label="Insert table" onClick={insertTable}><TableProperties /></ToolButton><ToolButton label="Insert image" disabled={uploading} onClick={() => imageInputRef.current?.click()}><ImagePlus /></ToolButton></div>
          </div>
          <div className="tiptap-editor"><EditorContent editor={editor} /></div>
          <input ref={imageInputRef} className="visually-hidden" type="file" accept="image/*" onChange={uploadImage} />
        </div>
        {previewOpen && <div className="markdown-preview"><p className="preview-label">Preview</p><MarkdownContent source={form.body || "_Your story preview will appear here._"} className="article-body" /></div>}
      </div>
    </div>
    <label className="check-label"><input type="checkbox" checked={form.is_breaking} onChange={(event) => update("is_breaking", event.target.checked)} /> Mark as breaking news</label>
    {(error || uploadError) && <p className="form-error">{error || uploadError}</p>}
    {success && <p className="form-success">{success}</p>}
    <div className="editor-actions"><button type="submit" className="button button-outline" disabled={submitting || uploading}>{submitting ? submittingLabel : submitLabel}</button>{canPublish && <button type="button" className="button button-dark" disabled={submitting || uploading} onClick={() => void submit(true)}>{submitting ? "Publishing..." : "Publish"}</button>}</div>
  </form>;
}
