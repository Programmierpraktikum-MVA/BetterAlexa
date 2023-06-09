FROM node:18-alpine AS base

FROM base AS builder
RUN apk add --no-cache libc6-compat
RUN apk update

WORKDIR /app

RUN yarn global add turbo
#TODO copy less
COPY . .
#TODO package doesnt exist yet
RUN turbo prune --scope=web --docker