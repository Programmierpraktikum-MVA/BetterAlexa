import { createTRPCRouter, protectedProcedure, publicProcedure } from "../trpc";

export const authRouter = createTRPCRouter({
  getSession: publicProcedure.query(({ ctx }) => {
    return ctx.session;
  }),
  createSpotifyAuth: protectedProcedure.mutation(({ ctx: { session } }) => {
    const params = new URLSearchParams({
      response_type: "code",
      client_id: process.env.SPOTIFY_CLIENT_ID as string,
      scope:
        "user-read-private user-modify-playback-state user-read-playback-state user-read-email",
      redirect_uri: `${process.env.NEXT_PUBLIC_BASE_URL}/api/callback/spotify`,
      state: session.email as string,
    });

    return `https://accounts.spotify.com/authorize?${params.toString()}`;
  }),
});
