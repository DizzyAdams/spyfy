# SpyFy Web — Next.js 15 (produção)
FROM node:20-alpine AS base

WORKDIR /app

# deps (usa package-lock.json via npm ci)
COPY package.json package-lock.json ./
RUN npm ci

# código
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
