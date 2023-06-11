import { type NextApiRequest, type NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const { code, state } = req.query;

  if (!state || !code) {
    res.status(400).send("Missing query parameters");
    return;
  }

  const response = (await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code: code as string,
      redirect_uri: `${process.env.NEXT_PUBLIC_BASE_URL}/api/callback/spotify`,
      client_id: process.env.SPOTIFY_CLIENT_ID as string,
      client_secret: process.env.SPOTIFY_CLIENT_SECRET as string,
    }).toString(),
  }).then((res) => res.json())) as {
    access_token: string;
    refresh_token: string;
    token_type: "Bearer";
    expires_in: number;
    scope: string;
  };

  res.setHeader("Set-Cookie", [
    `spotify-access-token=${response.access_token}; Path=/; HttpOnly`,
    `spotify-refresh-token=${response.refresh_token}; Path=/; HttpOnly`,
  ]);
  res.redirect("/");
}
