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
      └─ Sample api for frontend
packages
 ├─ api
 |   └─ tRPC v10 router definition
 ├─ auth
     └─ authentication using firebase auth
 └─ db
     └─ typesafe db-calls using Prisma -> optional, we can also just use mongodb client
```

## Quick Start

To get it running, follow the steps below:

### Setup dependencies

```txt
# Install dependencies
pnpm i

# Configure environment variables.
# There is an `.env.example` in the root directory you can use for reference
cp .env.example .env
```

## Deployment

### Next.js

#### Prerequisites

We will be using MongoDB as our database, and Firebase for our authentication.
<!-- TODO update -->
1. Create a MongoDB database and get the connection string. You can use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) for this.
2. Go to [Firebase Console](https://console.firebase.google.com/) and create a new Firebase project.
3. Create 3 apps for your Firebase project, a Web app, an Android app, and an iOS app. For the Android and iOS app, you can just use the package name from the Expo app (com.mva.betteralexa), you also need to generate a SHA1 for the Android app later.
4. Enable Firebase authentication with Google as a sign-in method. You can follow [this guide](https://firebase.google.com/docs/auth/web/google-signin) for this. We can add more sign-in method later.
5. Create a Service Account for your Firebase project. You can follow [this guide](https://firebase.google.com/docs/admin/setup#initialize-sdk) for this. Download the credentials file and paste the config to the `.env` file in the root directory, match it with our `.env.example`.
6. Get your Firebase config. You can follow [this guide](https://firebase.google.com/docs/web/setup#config-object) for this. Paste the config to the `.env` file in the root directory, match it with our `.env.example`.
7. To generate SHA1 for Expo Google sign in, you need to have an expo account. Link the project to your account, and generate a credentials with `expo credentials`
8. (OPTIONAL) if you want to use the current sample API, you need to have an OpenAI api key, paste it to the `.env` file in the root directory, match it with our `.env.example`.
## References

The stack originates from [create-t3-app](https://github.com/t3-oss/create-t3-app).
