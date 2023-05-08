import { audioRouter } from "./router/audio";
import { authRouter } from "./router/auth";
import { createTRPCRouter } from "./trpc";

export const appRouter = createTRPCRouter({
  auth: authRouter,
  audio: audioRouter,
});

// export type definition of API
export type AppRouter = typeof appRouter;
