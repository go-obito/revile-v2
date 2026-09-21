"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthProvider";
import { api } from "@/lib/api";

export function AdminNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, hasRole, accessToken } = useAuth();
  const [pendingCount, setPendingCount] = useState(0);
  useEffect(() => { if (accessToken && hasRole("editor")) api.getPendingCommentCount(accessToken).then(({ count }) => setPendingCount(count)).catch(() => undefined); }, [accessToken, hasRole]);
  const links = [
    ["Desk", "/admin"],
    ["Posts", "/admin/posts"],
    ["Write", "/admin/posts/new"],
    [pendingCount ? `Moderation (${pendingCount})` : "Moderation", "/admin/comments"],
    ...(hasRole("admin") ? [["Users", "/admin/users"]] : []),
  ];
  return <aside className="admin-nav"><Link className="wordmark" href="/">REVILE<span>.</span></Link><div className="admin-identity"><span>{user?.name}</span><small>{user?.role}</small></div><nav aria-label="Editorial navigation">{links.map(([label, href]) => <Link className={pathname === href || (href === "/admin/posts" && pathname.startsWith("/admin/posts/")) ? "active" : ""} href={href} key={href}>{label}</Link>)}</nav><button className="text-button" onClick={async () => { await logout(); router.push("/"); }}>Sign out</button></aside>;
}
