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
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://pymebot.azurewebsites.net/api/:path*',
      },
    ];
  },
};

export default nextConfig;