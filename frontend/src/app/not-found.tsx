import Link from "next/link";

export default function NotFound() {
  return <main className="center-state"><p className="eyebrow">404 / Not found</p><h1>That story moved.</h1><Link className="arrow-link" href="/">Back to the desk ↗</Link></main>;
}
