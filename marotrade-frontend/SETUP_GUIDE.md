# MaroTrade Frontend Setup Guide

## Prerequisites

- Node.js >= 22 (required for Tailwind CSS v4)
- npm or yarn
- PowerShell (for Windows users)

## Important: Directory Structure

The MaroTrade Intelligence project has a monorepo-like structure with:
- Root directory: `C:\Users\HP\Desktop\MaroTrade Intelligence`
- Frontend directory: `marotrade-frontend`

**⚠️ CRITICAL:** You must run all frontend commands from within the `marotrade-frontend` directory, NOT from the root directory. This is because:
1. The frontend has its own `package.json` and `node_modules`
2. There's a separate `package.json` at the root level for backend dependencies
3. Module resolution will fail if you run from the wrong directory

## Installation

1. Navigate to the frontend directory:
   ```powershell
   cd marotrade-frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

## Running the Development Server

### Option 1: Using PowerShell (Recommended)
```powershell
cd marotrade-frontend
npm run dev
```

### Option 2: Using the provided script
```powershell
.\marotrade-frontend\start-dev.ps1
```

### Option 3: Using Command Prompt
Double-click `marotrade-frontend\start-dev.bat`

## Development Commands

All commands must be run from the `marotrade-frontend` directory:

```powershell
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run linter
npm run lint
```

## Technology Stack

- **Framework:** Next.js 16.2.3 (with Turbopack)
- **Styling:** Tailwind CSS v4
- **Language:** TypeScript 5
- **State Management:** Zustand
- **Data Fetching:** TanStack React Query
- **UI Components:** Custom components + Lucide React icons
- **3D Graphics:** Three.js with React Three Fiber
- **Charts:** Recharts
- **Forms:** Zod validation

## Tailwind CSS v4 Configuration

This project uses Tailwind CSS v4, which has some differences from v3:

### Configuration Files
- `postcss.config.mjs` - Uses `@tailwindcss/postcss` plugin
- `tailwind.config.ts` - Legacy config for TypeScript support
- `src/app/globals.css` - Main CSS file with `@import 'tailwindcss'`

### CSS Variables
Tailwind v4 uses CSS variables for theming. All colors and design tokens are defined in `src/app/globals.css` using CSS custom properties.

### Key Features
- Dark mode support with CSS variables
- Custom animations and keyframes
- Glass morphism effects
- Custom scrollbar styling
- Responsive design utilities

## Troubleshooting

### Error: "Can't resolve 'tailwindcss'"
This error occurs when running the dev server from the wrong directory. Make sure you're in the `marotrade-frontend` directory:
```powershell
cd marotrade-frontend
npm run dev
```

### Module Resolution Issues
If you encounter module resolution errors:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Clear Next.js cache: delete `.next` folder
4. Restart the dev server

### Node.js Version Warnings
You may see warnings about Node.js version requirements. The project requires Node.js >= 22 for optimal performance with Tailwind CSS v4. If you're using an older version, consider upgrading.

## Project Structure

```
marotrade-frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── globals.css   # Global styles & Tailwind imports
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Home page
│   │   └── ...           # Other pages
│   ├── components/       # React components
│   │   ├── atoms/        # Small components
│   │   ├── molecules/    # Medium components
│   │   ├── organisms/    # Large components
│   │   └── ...           # Other components
│   ├── lib/              # Utilities and helpers
│   ├── store/            # Zustand stores
│   └── types/            # TypeScript types
├── public/               # Static assets
├── package.json          # Dependencies
├── tailwind.config.ts    # Tailwind configuration
├── next.config.ts        # Next.js configuration
├── tsconfig.json         # TypeScript configuration
└── postcss.config.mjs    # PostCSS configuration
```

## Environment Variables

Create a `.env.local` file in the `marotrade-frontend` directory for local environment variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# Add other environment variables as needed
```

## Build and Deployment

### Production Build
```powershell
npm run build
npm run start
```

### Docker Deployment
The project can be containerized using Docker. See the root `docker-compose.yml` for details.

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Zustand Documentation](https://zustand-demo.pmnd.rs/)

## Getting Help

If you encounter issues:
1. Check this guide first
2. Review the error messages carefully
3. Ensure you're in the correct directory
4. Try clearing caches and reinstalling dependencies
5. Check the project's main README for additional guidance