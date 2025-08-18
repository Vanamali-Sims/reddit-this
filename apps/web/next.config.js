/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    typedRoutes: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.API_BASE_URL || "http://localhost:8000"}/v1/:path*`,
      },
    ];
  },
  env: {
    API_BASE_URL: process.env.API_BASE_URL || "http://localhost:8000",
  },
};

module.exports = nextConfig;
