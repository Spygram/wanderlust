# syntax=docker/dockerfile:1

# ---------- Stage 1: build ----------
FROM node:21-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build
# ^ runs tsc, outputs compiled JS to dist/


# ---------- Stage 2: production ----------
FROM node:21-alpine AS production

ENV NODE_ENV=production
WORKDIR /app

# package.json is required at runtime — "type": "module" tells Node
# to treat dist/*.js as ESM
COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=builder /app/dist ./dist

USER node

EXPOSE 5000

CMD ["node", "dist/server.js"]
