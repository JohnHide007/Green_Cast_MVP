/** @type {import('next').NextConfig} */

// Backend production domain, hardcoded on purpose: NEXT_PUBLIC_API_URL on this
// project was pointing at the wrong host, which broke the proxy. The browser
// calls the same-origin "/be/*" path; Vercel proxies it to the backend below
// (no CORS, no env-var dependency). Update this string only if the backend
// project is renamed.
const BACKEND = "https://green-cast-mvp.vercel.app";

const nextConfig = {
  async rewrites() {
    return [
      { source: "/be/:path*", destination: `${BACKEND}/:path*` },
    ];
  },
};

export default nextConfig;
