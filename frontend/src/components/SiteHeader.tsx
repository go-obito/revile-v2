import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="shell header-inner">
        <Link className="wordmark" href="/">
          REVILE<span></span>
        </Link>
        <nav className="main-nav" aria-label="Main navigation">
          <Link href="/">Latest</Link>
          <Link href="/search">Search</Link>
          <Link className="nav-admin" href="/admin">Desk</Link>
        </nav>
      </div>
      <div className="ticker" aria-label="Breaking news">
        <div className="shell ticker-inner"><span className="ticker-label">BREAKING</span><span>Independent reporting on the technology shaping tomorrow.</span></div>
      </div>
    </header>
  );
}
