import { type NextApiRequest, type NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  try {
    // Check if request method is POST
    if (req.method !== "POST") {
      res.status(405).send("Method Not Allowed");
      return;
    }

    // Parse incoming data as binary
    const data = (await req.body) as Buffer;
    const audioBlob = new Blob([data], { type: "audio/webm" });
    console.log("audioBlob", audioBlob.size);

    // Here, you can process the audio data as needed. For example, you can
    // use a third-party library like `ffmpeg` to convert the audio to a
    // different format, analyze the audio data, etc.

    // Respond with success message
    res.status(200).send("Audio processed successfully");
  } catch (error) {
    console.error(error);
    res.status(500).send("Internal Server Error");
  }
}
