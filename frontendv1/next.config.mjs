/** @type {import('next').NextConfig} */
const configuredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
const BACKEND_ORIGIN =
  !configuredApiBaseUrl || configuredApiBaseUrl.startsWith("/")
    ? "http://127.0.0.1:8000"
    : configuredApiBaseUrl.replace(/\/api\/v1\/?$/, "");

const nextConfig = {
  reactStrictMode: true,
  allowedDevOrigins: ["127.0.0.1", "localhost"],
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_ORIGIN}/api/:path*`,
      },
    ];
  },
  async redirects() {
    return [
      // Legacy path redirects can be added here
      // { source: '/old-path', destination: '/new-path', permanent: true },
    ];
  },
};

export default nextConfig;
