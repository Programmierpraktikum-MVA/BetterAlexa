import { authRouter } from "./router/auth";
import { microserviceRouter } from "./router/microservice";
import { createTRPCRouter } from "./trpc";

export const appRouter = createTRPCRouter({
  auth: authRouter,
  microservice: microserviceRouter,
});

// export type definition of API
export type AppRouter = typeof appRouter;
