import { z } from "zod";

import { createTRPCRouter, protectedProcedure } from "../trpc";

export const microserviceRouter = createTRPCRouter({
  speechToText: protectedProcedure
    .input(
      z.string().startsWith("data:audio/webm;base64,", "Invalid audio data"),
    )
    .mutation(async ({ input }) => {
      const data = input.replace("data:audio/webm;base64,", "");
      const audioBlob = Buffer.from(data, "base64");

      const result = await fetch(process.env.SPEECH_TO_TEXT_URL as string, {
        method: "POST",
        body: audioBlob,
      });

      if (!result.ok) {
        throw new Error("Failed to process audio");
      }

      return (await result.json()) as { result: { text: string } };
    }),
  commandToAction: protectedProcedure
    .input(z.string().min(1, "Invalid request"))
    .mutation(async ({ input, ctx: { cookies } }) => {
      const result = await fetch(process.env.COMMAND_TO_ACTION_URL as string, {
        method: "POST",
        headers: {
          "x-spotify-access-token": cookies?.["spotify-access-token"] as string,
        },
        body: input,
      });

      if (!result.ok) {
        throw new Error("Failed to process action");
      }

      return (await result.json()) as { result: { text: string } };
    }),
  textToSpeech: protectedProcedure
    .input(z.string().min(1, "Invalid request"))
    .mutation(async ({ input }) => {
      const result = await fetch(process.env.TEXT_TO_SPEECH_URL as string, {
        method: "POST",
        body: input,
      });

      if (!result.ok) {
        throw new Error("Failed to generate speech");
      }

      const audioBuffer = await result.arrayBuffer();
      const audioData = Buffer.from(audioBuffer).toString("base64");

      return { result: { base64: audioData } };
    }),
});
