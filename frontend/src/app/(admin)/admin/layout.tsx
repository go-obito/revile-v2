import type { ReactNode } from "react";
import { AdminGate } from "@/components/AdminGate";
import { AdminNav } from "@/components/AdminNav";

export default function AdminLayout({ children }: { children: ReactNode }) {
  return <AdminGate><div className="admin-frame"><AdminNav />{children}</div></AdminGate>;
}
