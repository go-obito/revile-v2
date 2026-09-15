"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthProvider";

export function AdminGate({ children }: { children: ReactNode }) {
  const { loading, user, hasRole } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && (!user || !hasRole("admin", "editor", "author"))) router.replace(`/login?next=${encodeURIComponent(pathname)}`);
  }, [hasRole, loading, pathname, router, user]);

  if (loading || !user || !hasRole("admin", "editor", "author")) return <main className="center-state"><p>Checking desk access...</p></main>;
  return <>{children}</>;
}
