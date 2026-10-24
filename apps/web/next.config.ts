import type { NextConfig } from "next";

// FastAPI base URL. The browser only ever talks to Next.js; /api/* is proxied here,
// so the app has a single origin (no CORS, first-party session cookies).
const apiUrl = process.env.API_URL ?? "http://localhost:8010";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/api/:path*` }];
  },
};

export default nextConfig;
