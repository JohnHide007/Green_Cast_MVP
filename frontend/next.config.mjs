/** @type {import('next').NextConfig} */

// Backend origin. Set NEXT_PUBLIC_API_URL in Vercel (frontend project).
// The browser never calls this directly — it calls the same-origin "/be"
// path below, which Vercel proxies to the backend. That removes both the
// localhost-fallback problem and any CORS friction for client-side fetches.
const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const nextConfig = {
  async rewrites() {
    return [
      { source: "/be/:path*", destination: `${BACKEND}/:path*` },
    ];
  },
};

export default nextConfig;
