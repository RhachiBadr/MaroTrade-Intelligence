import type { NextConfig } from 'next'
import path from 'path'
import { fileURLToPath } from 'url'

// Get the directory name of this config file
const configDir = path.dirname(fileURLToPath(import.meta.url))

const nextConfig: NextConfig = {
  // Force Turbopack to use marotrade-frontend as root (not the monorepo parent with another lockfile)
  turbopack: {
    root: configDir,
  },
  
  // Ensure webpack resolves modules from this directory only
  webpack: (config, { isServer }) => {
    // Add explicit resolve roots to prevent looking in parent directories
    config.resolve.modules = [
      path.join(configDir, 'node_modules'),
      'node_modules'
    ]
    return config
  },
}

export default nextConfig
