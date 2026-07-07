# 1. Setup: Base image with Node.js and working directory
FROM node:22-alpine AS base
WORKDIR /app
RUN corepack enable pnpm

# 2. Layer for dependencies (Target: deps)
FROM base AS deps
RUN apk add --no-cache libc6-compat
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

# ==========================================
# 3. Layer for Development (Target: dev)
#    We use volumes to mount the source code for live development.
# ==========================================
FROM deps AS dev
EXPOSE 3000
CMD ["pnpm", "dev"]

# ==========================================
# 4. Layer for Building (Target: builder)
#    This layer is used to build the application for production.
# ==========================================
FROM deps AS builder
ENV NEXT_TELEMETRY_DISABLED=1
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN pnpm build

# ==========================================
# 5. Layer for Production (Target: runner)
# ==========================================
FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["pnpm", "start"]