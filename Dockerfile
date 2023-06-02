FROM node:18.16.0

WORKDIR /usr/src/app

COPY package.json ./
COPY pnpm-lock.yaml ./

COPY apps/nextjs/package.json ./apps/nextjs/package.json

COPY apps/sample/package.json apps/sample/requirements.txt ./apps/sample/

# RUN npm install -g pnpm
RUN curl -f https://get.pnpm.io/v6.16.js | node - add --global pnpm

RUN pnpm install --frozen-lockfile --prod

RUN ls
RUN ls ./apps/nextjs
RUN ls ./apps/sample



# WORKDIR /usr/src/app/apps/sample

# RUN pnpm install 

# WORKDIR /usr/src/app/apps/nextjs

# RUN pnpm install