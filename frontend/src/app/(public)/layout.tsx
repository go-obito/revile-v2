import type { ReactNode } from "react";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { NewsletterForm } from "@/components/NewsletterForm";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return <><SiteHeader />{children}<footer className="site-footer"><div className="shell footer-grid"><div><strong className="footer-wordmark">REV<span>ILE</span>.</strong><p>Technology, reported with clarity and conviction.</p></div><div className="footer-links"><div><p className="footer-label">Sections</p><Link href="/">Latest stories</Link><Link href="/search">Search reporting</Link></div><div><p className="footer-label">The desk</p><Link href="/admin">Editorial desk</Link><Link href="/newsletter/confirmed">Newsletter</Link></div></div><div><p className="footer-label">The briefing</p><p className="footer-copy">A focused read on what is changing and why it matters.</p><NewsletterForm compact /></div></div><div className="shell footer-bottom"><span>© {new Date().getFullYear()} Revile</span><span>Independent technology journalism</span></div></footer></>;
}
