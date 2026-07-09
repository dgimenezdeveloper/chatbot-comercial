/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', 
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.googleusercontent.com",
        pathname: "/**",
      },
      {
        protocol: "http",
        hostname: "googleusercontent.com",
        pathname: "/**",
      },
    ],
  },
  
  // Apuntamos el proxy invisible a la url de tu backend en Azure
  // (Actualizado para no interferir con las rutas internas de NextAuth /api/auth/*)
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'https://pymebot.azurewebsites.net/api/v1/:path*',
      },
    ];
  },
};

export default nextConfig;