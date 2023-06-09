FROM node:18.16.0-alpine AS base

FROM base AS builder
RUN apk add --no-cache libc6-compat
RUN apk update

WORKDIR /app

RUN npm install -g pnpm
RUN mkdir -p ~/.pnpm/store
RUN export PNPM_HOME=~/.pnpm/store
ENV PATH="${PATH}:/opt/gtk/bin"

RUN pnpm add turbo --global
#TODO copy less
COPY . .    
#TODO package doesnt exist yet
RUN turbo prune --scope=nextjs --docker