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

<!-- ## FAQ

### Can you include Solito?

No. Solito will not be included in this repo. It is a great tool if you want to share code between your Next.js and Expo app. However, the main purpose of this repo is not the integration between Next.js and Expo - it's the codesplitting of your T3 App into a monorepo, the Expo app is just a bonus example of how you can utilize the monorepo with multiple apps but can just as well be any app such as Vite, Electron, etc.

Integrating Solito into this repo isn't hard, and there are a few [offical templates](https://github.com/nandorojo/solito/tree/master/example-monorepos) by the creators of Solito that you can use as a reference.

### What auth solution should I use instead of Next-Auth.js for Expo?

I've left this kind of open for you to decide. Some options are [Clerk](https://clerk.dev), [Supabase Auth](https://supabase.com/docs/guides/auth), [Firebase Auth](https://firebase.google.com/docs/auth/) or [Auth0](https://auth0.com/docs). Note that if you're dropping the Expo app for something more "browser-like", you can still use Next-Auth.js for those. [See an example in a Plasmo Chrome Extension here](https://github.com/t3-oss/create-t3-turbo/tree/chrome/apps/chrome).

The Clerk.dev team even made an [official template repository](https://github.com/clerkinc/t3-turbo-and-clerk) integrating Clerk.dev with this repo.

During Launch Week 7, Supabase [announced their fork](https://supabase.com/blog/launch-week-7-community-highlights#t3-turbo-x-supabase) of this repo integrating it with their newly announced auth improvements. You can check it out [here](https://github.com/supabase-community/create-t3-turbo).

### Does this pattern leak backend code to my client applications?

No, it does not. The `api` package should only be a production dependency in the Next.js application where it's served. The Expo app, and all other apps you may add in the future, should only add the `api` package as a dev dependency. This lets you have full typesafety in your client applications, while keeping your backend code safe.

If you need to share runtime code between the client and server, such as input validation schemas, you can create a separate `shared` package for this and import on both sides. -->

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

1. Create a MongoDB database and get the connection string. You can use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) for this.
2. Go to [Firebase Console](https://console.firebase.google.com/) and create a new Firebase project.
3. Create 3 apps for your Firebase project, a Web app, an Android app, and an iOS app. For the Android and iOS app, you can just use the package name from the Expo app (com.mva.betteralexa), you also need to generate a SHA1 for the Android app later.
4. Enable Firebase authentication with Google as a sign-in method. You can follow [this guide](https://firebase.google.com/docs/auth/web/google-signin) for this. We can add more sign-in method later.
5. Create a Service Account for your Firebase project. You can follow [this guide](https://firebase.google.com/docs/admin/setup#initialize-sdk) for this. Download the credentials file and paste the config to the `.env` file in the root directory, match it with our `.env.example`.
6. Get your Firebase config. You can follow [this guide](https://firebase.google.com/docs/web/setup#config-object) for this. Paste the config to the `.env` file in the root directory, match it with our `.env.example`.
7. To generate SHA1 for Expo Google sign in, you need to have an expo account. Link the project to your account, and generate a credentials with `expo credentials`
8. (OPTIONAL) if you want to use the current sample API, you need to have an OpenAI api key, paste it to the `.env` file in the root directory, match it with our `.env.example`.

**Please note that the Next.js application with tRPC must be deployed in order for the Expo app to communicate with the server in a production environment.**

#### Deploy to Vercel

Let's deploy the Next.js application to [Vercel](https://vercel.com/). If you have ever deployed a Turborepo app there, the steps are quite straightforward. You can also read the [official Turborepo guide](https://vercel.com/docs/concepts/monorepos/turborepo) on deploying to Vercel.

1. Create a new project on Vercel, select the `apps/nextjs` folder as the root directory and apply the following build settings:

<img width="927" alt="Vercel deployment settings" src="https://user-images.githubusercontent.com/11340449/201974887-b6403a32-5570-4ce6-b146-c486c0dbd244.png">

> The install command filters out the expo package and saves a few second (and cache size) of dependency installation. The build command makes us build the application using Turbo.

1. Add your environment variables (you can paste the .env file to vercel).

2. Done! Your app should successfully deploy. Assign your domain and use that instead of `localhost` for the `url` in the Expo app so that your Expo app can communicate with your backend when you are not in development.

## References

The stack originates from [create-t3-app](https://github.com/t3-oss/create-t3-app).
