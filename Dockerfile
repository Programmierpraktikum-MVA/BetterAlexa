FROM node:16 

WORKDIR /usr/src/app

COPY package.json ./
COPY pnpm-lock.yaml ./

COPY apps/nextjs/package.json ./apps/nextjs/package.json

COPY apps/sample/package.json apps/sample/requirements.txt ./apps/sample/

RUN ls 
RUN ls apps/sample
RUN ls apps/nextjs