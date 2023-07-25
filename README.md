# BetterAlexa Monorepo

## About

Welcome to BetterAlexa monorepo, we use create t3 turbo to create this monorepo.

Folder structure:

```txt
.github
  └─ workflows
        └─ CI with pnpm cache setup
.vscode
  └─ Recommended extensions and settings for VSCode users
apps
  ├─ command-to-action
  |   ├─ Flask
  |   ├─ OpenAI GPT
  |   └─ Langchain / OpenAI Functioncalling
  ├─ expo
  |   ├─ Expo SDK 48
  |   ├─ React Native using React 18
  |   ├─ Navigation using Expo Router
  |   ├─ Tailwind using Nativewind
  |   └─ Typesafe API calls using tRPC
  ├─ next.js
  |   ├─ Next.js 13
  |   ├─ React 18
  |   ├─ Tailwind CSS
  |   └─ E2E Typesafe API Server & Client
  └─ sample
      ├─ Flask
      ├─ Google Text2Speech
      └─ OpenAI Whisper
packages
 ├─ api
 |   └─ tRPC v10 router definition
 ├─ auth
 |   └─ Authentication using Firebase Auth
 └─ db
     └─ Redis
```
<!-- Test -->
## Quick Start

To get it running, follow the steps below:

### Setup dependencies

```sh
# Install dependencies
pnpm i

# Configure environment variables.
# There is an `.env.example` in the root directory you can use for reference
cp .env.example .env
```

## Deployment

### Next.js

#### Prerequisites

We are using Redis as our database, and Firebase for our authentication. We're running everything on a VPS.

- Create a [Redis DB](https://redis.io/docs/getting-started/installation/install-redis-on-linux/) on your VPS.
- Go to [Firebase Console](https://console.firebase.google.com/) and create a new Firebase project.
  - Create 3 apps for your Firebase project, a Web app, an Android app, and an iOS app. For the Android and iOS app, you can just use the package name from the Expo app (com.mva.betteralexa), you also need to generate a SHA1 for the Android app later.
  - Enable Firebase authentication with Google as a sign-in method. You can follow [this guide](https://firebase.google.com/docs/auth/web/google-signin) for this. We can add more sign-in method later.
  - Create a Service Account for your Firebase project. You can follow [this guide](https://firebase.google.com/docs/admin/setup#initialize-sdk) for this. Download the credentials file and paste the config to the `.env` file in the root directory, match it with our `.env.example`.
  - Get your Firebase config. You can follow [this guide](https://firebase.google.com/docs/web/setup#config-object) for this. Paste the config to the `.env` file in the root directory, match it with our `.env.example`.
- To generate SHA1 for Expo Google sign in, you need to have an expo account. Link the project to your account, and generate a credentials with `expo credentials`
- (OPTIONAL) if you want to use the current sample API, you need to have an OpenAI api key, paste it to the `.env` file in the root directory, match it with our `.env.example`.
- (OPTIONAL) if you want to use the spotify:
  - Go to [Spotify Dashboard](https://developer.spotify.com/dashboard) and create an app
  - put `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in your `.env`
  - If you dont want to use it, remove the tool from [cta](./apps/command-to-action/api/)

## Development
Use `pnpm dev`

## Production
Use `docker compose up`

## References

The stack originates from [create-t3-app](https://github.com/t3-oss/create-t3-app).
