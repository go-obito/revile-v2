"use client";

import { Printer, Share2, Check, Link as LinkIcon } from "lucide-react";
import { useState } from "react";

export function ArticleActions({ title }: { title: string }) {
  const [copied, setCopied] = useState(false);
  async function share() {
    const url = window.location.href;
    if (navigator.share) {
      try { await navigator.share({ title, url }); return; } catch { /* Fall through to copy when sharing is dismissed or unavailable. */ }
    }
    try { await navigator.clipboard.writeText(url); setCopied(true); window.setTimeout(() => setCopied(false), 1800); } catch { window.prompt("Copy this link:", url); }
  }
  return <div className="article-actions" aria-label="Article tools"><button type="button" onClick={share}>{copied ? <Check aria-hidden="true" /> : <Share2 aria-hidden="true" />}<span>{copied ? "Copied" : "Share"}</span></button><button type="button" onClick={() => window.print()}><Printer aria-hidden="true" /><span>Print</span></button><span className="visually-hidden"><LinkIcon />Share or print this article</span></div>;
}
