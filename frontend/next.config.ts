import type { NextConfig } from "next";

const backendUrl = (process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
const backendApiUrl = backendUrl.endsWith("/api/v1") ? backendUrl : `${backendUrl}/api/v1`;

const nextConfig: NextConfig = {
  poweredByHeader: false,
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: `${backendApiUrl}/:path*` }];
  },
};

export default nextConfig;
