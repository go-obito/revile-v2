"use client";

import Link from "next/link";
import { Menu, Search, X } from "lucide-react";
import { useEffect, useState } from "react";
import { api, type CategoryRead } from "@/lib/api";

export function SiteHeader() {
  const [categories, setCategories] = useState<CategoryRead[]>([]);
  const [open, setOpen] = useState(false);
  useEffect(() => { api.getCategories().then(setCategories).catch(() => undefined); }, []);
  const close = () => setOpen(false);
  return <header className="site-header">
    <div className="utility-bar"><div className="shell utility-inner"><span>Independent technology journalism</span><span>{new Intl.DateTimeFormat("en-US", { weekday: "long", month: "long", day: "numeric" }).format(new Date())}</span></div></div>
    <div className="shell header-inner">
      <Link className="wordmark" href="/" onClick={close}>REVILE<span>.</span></Link>
      <nav className="main-nav" aria-label="Primary navigation"><Link href="/">Latest</Link><Link href="/search">Search</Link><Link className="nav-admin" href="/admin">Desk</Link></nav>
      <button className="mobile-menu-button" type="button" onClick={() => setOpen((value) => !value)} aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open}>{open ? <X /> : <Menu />}</button>
    </div>
    <div className="section-nav-wrap"><nav className="shell section-nav" aria-label="Publication sections">{categories.map((category) => <Link key={category.id} href={`/categories/${category.slug}`}>{category.name}</Link>)}<Link className="section-nav-search" href="/search" aria-label="Search Revile"><Search aria-hidden="true" /></Link></nav></div>
    {open && <nav className="mobile-nav" aria-label="Mobile navigation"><Link href="/" onClick={close}>Latest stories</Link>{categories.map((category) => <Link key={category.id} href={`/categories/${category.slug}`} onClick={close}>{category.name}</Link>)}<Link href="/search" onClick={close}>Search</Link><Link href="/admin" onClick={close}>Editorial desk</Link></nav>}
    <div className="ticker" aria-label="Breaking news"><div className="shell ticker-inner"><span className="ticker-label">Live desk</span><span>Independent reporting on the technology shaping tomorrow.</span></div></div>
  </header>;
}
