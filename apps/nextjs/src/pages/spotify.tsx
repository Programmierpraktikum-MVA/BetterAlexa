/* eslint-disable @typescript-eslint/no-misused-promises */
import { type NextPage } from "next";
import Head from "next/head";
import { useRouter } from "next/router";

import { useSession } from "@acme/auth";

import { api } from "~/utils/api";

const SpotifyConnect: NextPage = () => {
  const session = useSession();
  const router = useRouter();
  const { mutateAsync } = api.auth.createSpotifyAuth.useMutation();
  return (
    <>
      <Head>
        <title>BetterAlexa | Connect Spotify</title>
        <meta
          name="description"
          content="BetterAlexa - OpenAI with Langchain Integration"
        />
        <link
          rel="apple-touch-icon"
          sizes="180x180"
          href="/apple-touch-icon.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="32x32"
          href="/favicon-32x32.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="16x16"
          href="/favicon-16x16.png"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#0891b2" />
        <link rel="manifest" href="/site.webmanifest" />
      </Head>
      <main className="flex h-screen flex-col items-center bg-gradient-to-b from-[#2e026d] to-[#15162c] text-white">
        <div className="container mt-12 flex flex-col items-center justify-center gap-4 px-4 py-8">
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-[5rem]">
            Better<span className="text-pink-400">Alexa</span>
          </h1>
          {session.loading && <div>Loading...</div>}
          {!session.loading && !session.user && (
            <span className="ml-2 text-sm font-semibold text-gray-400">
              You need to sign in first!
            </span>
          )}
          {session.user && (
            <button
              className="rounded-lg bg-gray-700 px-3 py-2 text-sm font-semibold text-white hover:bg-gray-800"
              onClick={async () => {
                const url = await mutateAsync();
                void router.push(url);
              }}
            >
              Connect Spotify
            </button>
          )}
        </div>
      </main>
    </>
  );
};

export default SpotifyConnect;
