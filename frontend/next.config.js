/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  async rewrites() {
    return [
      {
        source: '/api/mcp/:path*',
        destination: 'http://localhost:8051/:path*',
      },
    ]
  },
  env: {
    MCP_SERVER_URL: process.env.MCP_SERVER_URL || 'http://localhost:8051',
  },
}

module.exports = nextConfig
