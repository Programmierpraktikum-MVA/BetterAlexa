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

      const result = await fetch(`${process.env.SAMPLE_URL}/speech-to-text`, {
        method: "POST",
        body: audioBlob,
      });

      if (!result.ok) {
        throw new Error("Failed to process audio");
      }

      return (await result.json()) as { result: { text: string } };
    }),
  callToAction: protectedProcedure
    .input(z.string().min(1, "Invalid request"))
    .mutation(async ({ input }) => {
      const result = await fetch(`${process.env.SAMPLE_URL}/call-to-action`, {
        method: "POST",
        body: input,
      });

      if (!result.ok) {
        throw new Error("Failed to process action");
      }

      return (await result.json()) as { result: { text: string } };
    }),
});
