import { httpBatchLink, loggerLink } from "@trpc/client";
import { createTRPCNext } from "@trpc/next";
import superjson from "superjson";

import type { AppRouter } from "@acme/api";
import { auth } from "@acme/auth";

const getBaseUrl = () => {
  if (typeof window !== "undefined") return ""; // browser should use relative url
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`; // SSR should use vercel url

  return `http://localhost:3000`; // dev SSR should use localhost
};

export const api = createTRPCNext<AppRouter>({
  config() {
    return {
      queryClientConfig: {
        defaultOptions: {
          queries: {
            retry: false,
          },
          mutations: {
            retry: false,
          },
        },
      },
      transformer: superjson,
      links: [
        loggerLink({
          enabled: (opts) =>
            process.env.NODE_ENV === "development" ||
            (opts.direction === "down" && opts.result instanceof Error),
        }),
        httpBatchLink({
          url: `${getBaseUrl()}/api/trpc`,
          async headers() {
            const token = (await auth.currentUser?.getIdToken()) || "";
            return token
              ? {
                  Authorization: `Bearer ${token}`,
                }
              : {};
          },
        }),
      ],
    };
  },
  ssr: false,
});

export { type RouterInputs, type RouterOutputs } from "@acme/api";
