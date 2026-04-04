# Ink & Quill Frontend V1

React rebuild of the Ink & Quill application using Next.js 15 with React 19.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5.6 (strict mode)
- **Styling**: Tailwind CSS 3.4
- **State**: TanStack React Query v5
- **Forms**: React Hook Form + Zod + @hookform/resolvers
- **Components**: Radix UI primitives + Class Variance Authority
- **Testing**: Playwright E2E

## Getting Started

### Prerequisites

- Node.js 18+
- npm or pnpm

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Opens at http://localhost:3000

### Build

```bash
npm run build
```

### Type Check

```bash
npm run typecheck
```

### Lint

```bash
npm run lint
```

### E2E Tests

```bash
npm run test:e2e
```

With UI:

```bash
npm run test:e2e:ui
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

## Project Structure

```
frontendv1/
├── app/                    # Next.js App Router pages
│   ├── auth/              # Authentication routes
│   ├── storytelling/      # Storytelling app surface
│   ├── chatbot/          # Chatbot app surface
│   ├── care-circle-*/   # Care circle app surfaces
│   └── layout.tsx        # Root layout
├── components/
│   ├── platform/         # Platform routing components
│   ├── providers/        # React context providers
│   ├── shell/            # App shell (nav, footer, etc.)
│   └── ui/               # Reusable UI components
├── lib/
│   ├── api.ts           # API client functions
│   ├── apps/            # App definitions
│   ├── types.ts         # TypeScript types
│   └── utils.ts         # Utility functions
├── tests/e2e/            # Playwright E2E tests
└── public/              # Static assets
```

## App Surfaces

The frontend supports multiple application surfaces:

- **Storytelling** (`/storytelling/*`) - Creative authoring
- **Chatbot** (`/chatbot/*`) - AI chatbot
- **Care Circle Family** (`/care-circle-family/*`) - Family care coordination
- **Care Circle Patient** (`/care-circle-patient/*`) - Patient-facing care features

## Design System

Custom Tailwind theme with Ink & Quill branding:

- **Colors**: ink (warm brown), ember (orange accent), forest (green), mist (gray-blue), paper (cream)
- **Typography**: Georgia/Cambria for serif, Garamond for display
- **Components**: Button variants, form fields, cards, modals, data tables, empty states

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run typecheck` | Run TypeScript check |
| `npm run test:e2e` | Run Playwright tests |
| `npm run test:e2e:ui` | Run Playwright with UI |
