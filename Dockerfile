FROM node:18.16.0-alpine AS base

FROM base AS builder
RUN apk add --no-cache libc6-compat openssl1.1-compat
RUN apk update

WORKDIR /app

COPY package.json .
COPY pnpm-lock.yaml .
COPY apps/nextjs/package.json ./apps/nextjs/
COPY packages/api/package.json ./packages/api/
COPY packages/auth/package.json ./packages/auth/
COPY packages/config/tailwind/package.json ./packages/config/tailwind/
COPY packages/config/eslint/package.json ./packages/config/eslint/
COPY packages/db/package.json ./packages/db/

RUN yarn global add pnpm 
RUN pnpm add turbo --global
#TODO copy less
COPY . .    
#TODO package doesnt exist yet
RUN turbo prune --scope=nextjs --docker