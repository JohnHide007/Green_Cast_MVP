/** @type {import('next').NextConfig} */

// Backend origin. Set NEXT_PUBLIC_API_URL in Vercel (frontend project).
// The browser never calls this directly — it calls the same-origin "/be"
// path below, which Vercel proxies to the backend. That removes both the
// localhost-fallback problem and any CORS friction for client-side fetches.
// Backend production domain (auto-tracks latest backend deploy). Override with
// NEXT_PUBLIC_API_URL if you ever rename the backend project.
const BACKEND = process.env.NEXT_PUBLIC_API_URL || "https://green-cast-mvp.vercel.app";

const nextConfig = {
  async rewrites() {
    return [
      { source: "/be/:path*", destination: `${BACKEND}/:path*` },
    ];
  },
};

export default nextConfig;
