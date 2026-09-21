import type { ReactNode } from "react";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { NewsletterForm } from "@/components/NewsletterForm";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return <><SiteHeader />{children}<footer className="site-footer"><div className="shell footer-grid"><div><strong className="footer-wordmark">REVILE.</strong><p>Technology, reported with clarity and conviction.</p></div><div><p className="footer-label">The briefing</p><p className="footer-copy">A focused read on what is changing and why it matters.</p><NewsletterForm compact /></div><div className="footer-meta"><Link href="/search">Search reporting</Link><Link href="/admin">Editorial desk</Link><span>© {new Date().getFullYear()} Revile</span></div></div></footer></>;
}
