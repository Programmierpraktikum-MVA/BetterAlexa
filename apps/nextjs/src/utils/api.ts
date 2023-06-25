import { httpBatchLink, loggerLink } from "@trpc/client";
import { createTRPCNext } from "@trpc/next";
import superjson from "superjson";

import type { AppRouter } from "@acme/api";
import { auth } from "@acme/auth";

import { toast } from "~/components/ui/toast/use-toast";

const getBaseUrl = () => {
  // eslint-disable-next-line turbo/no-undeclared-env-vars
  if (process.env.IS_EXTENSION) {
    if (!process.env.NEXT_PUBLIC_BASE_URL)
      throw new Error("Missing NEXT_PUBLIC_BASE_URL for building extension!");
    return process.env.NEXT_PUBLIC_BASE_URL;
  }
  if (typeof window !== "undefined") return ""; // browser should use relative url
  if (process.env.NEXT_PUBLIC_BASE_URL) return process.env.NEXT_PUBLIC_BASE_URL;
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`; // SSR should use vercel url

  return `http://localhost:3000`; // dev SSR should use localhost
};

function handleError<T>(err: T) {
  if (err instanceof Error) {
    toast({
      variant: "destructive",
      title: "Uh oh! Something went wrong.",
      description: err.message,
    });
  }
}

export const api = createTRPCNext<AppRouter>({
  config() {
    return {
      queryClientConfig: {
        defaultOptions: {
          queries: {
            retry: false,
            onError: handleError,
          },
          mutations: {
            retry: false,
            onError: handleError,
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
