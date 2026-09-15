import type { ReactNode } from "react";
import { SiteHeader } from "@/components/SiteHeader";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return <><SiteHeader />{children}<footer className="site-footer"><div className="shell footer-inner"><strong>REVILE.</strong><span>Technology, reported with intent.</span><span>© {new Date().getFullYear()} Revile</span></div></footer></>;
}
