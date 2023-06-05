FROM node:18.16.0

WORKDIR /app

COPY . .

RUN npm i -g pnpm

RUN apt -yqq update

RUN apt install -yqq python

RUN apt install -yqq python3-pip

RUN pnpm install
RUN pnpm db:generate

RUN pnpm build

CMD ["pnpm", "start"] 