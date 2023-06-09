import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  /**
   * Specify your server-side environment variables schema here. This way you can ensure the app isn't
   * built with invalid env vars.
   */
  server: {
    DATABASE_URL: z.string().url(),
    NODE_ENV: z.enum(["development", "test", "production"]),
    FIREBASE_PROJECT_ID: z.string(),
    FIREBASE_CLIENT_EMAIL: z.string().email(),
    FIREBASE_PRIVATE_KEY: z.string(),
    SPEECH_TO_TEXT_URL: z.string().url(),
    COMMAND_TO_ACTION_URL: z.string().url(),
    TEXT_TO_SPEECH_URL: z.string().url(),
    SPOTIFY_CLIENT_ID: z.string(),
    SPOTIFY_CLIENT_SECRET: z.string(),
  },
  /**
   * Specify your client-side environment variables schema here.
   * For them to be exposed to the client, prefix them with `NEXT_PUBLIC_`.
   */
  client: {
    NEXT_PUBLIC_IS_EXTENSION: z.string().optional(),
    NEXT_PUBLIC_API_KEY: z.string(),
    NEXT_PUBLIC_AUTH_DOMAIN: z.string(),
    NEXT_PUBLIC_PROJECT_ID: z.string(),
    NEXT_PUBLIC_STORAGE_BUCKET: z.string(),
    NEXT_PUBLIC_MESSAGING_SENDER_ID: z.string(),
    NEXT_PUBLIC_APP_ID: z.string(),
    NEXT_PUBLIC_BASE_URL: z.string().url(),
  },
  /**
   * Destructure all variables from `process.env` to make sure they aren't tree-shaken away.
   */
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    NODE_ENV: process.env.NODE_ENV,
    FIREBASE_PROJECT_ID: process.env.FIREBASE_PROJECT_ID,
    FIREBASE_CLIENT_EMAIL: process.env.FIREBASE_CLIENT_EMAIL,
    FIREBASE_PRIVATE_KEY: process.env.FIREBASE_PRIVATE_KEY,
    SPEECH_TO_TEXT_URL: process.env.SPEECH_TO_TEXT_URL,
    COMMAND_TO_ACTION_URL: process.env.COMMAND_TO_ACTION_URL,
    TEXT_TO_SPEECH_URL: process.env.TEXT_TO_SPEECH_URL,
    SPOTIFY_CLIENT_ID: process.env.SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET: process.env.SPOTIFY_CLIENT_SECRET,
    NEXT_PUBLIC_IS_EXTENSION: process.env.NEXT_PUBLIC_IS_EXTENSION,
    NEXT_PUBLIC_API_KEY: process.env.NEXT_PUBLIC_API_KEY,
    NEXT_PUBLIC_AUTH_DOMAIN: process.env.NEXT_PUBLIC_AUTH_DOMAIN,
    NEXT_PUBLIC_PROJECT_ID: process.env.NEXT_PUBLIC_PROJECT_ID,
    NEXT_PUBLIC_STORAGE_BUCKET: process.env.NEXT_PUBLIC_STORAGE_BUCKET,
    NEXT_PUBLIC_MESSAGING_SENDER_ID:
      process.env.NEXT_PUBLIC_MESSAGING_SENDER_ID,
    NEXT_PUBLIC_APP_ID: process.env.NEXT_PUBLIC_APP_ID,
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL,
  },
});
