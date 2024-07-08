/* eslint-disable @typescript-eslint/no-misused-promises */
import { type NextPage } from "next";
import { useRouter } from "next/router";

import { useSession } from "@acme/auth";

import { api } from "~/utils/api";
import RouteGuard from "~/components/RouteGuard";

const SpotifyConnect: NextPage = () => {
  const session = useSession();
  const router = useRouter();
  const { mutateAsync } = api.auth.createSpotifyAuth.useMutation();
  return (
    <>
      <RouteGuard />

      <div>
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
    </>
  );
};

export default SpotifyConnect;