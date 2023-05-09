import { z } from "zod";

import { createTRPCRouter, protectedProcedure } from "../trpc";

type ProcessOutput = {
  result: {
    text: string;
  };
};

export const audioRouter = createTRPCRouter({
  process: protectedProcedure
    .input(
      z.string().startsWith("data:audio/webm;base64,", "Invalid audio data"),
    )
    .mutation(async ({ input }) => {
      const data = input.replace("data:audio/webm;base64,", "");
      const audioBlob = Buffer.from(data, "base64");

      const result = await fetch(`${process.env.S2T_URL}/process`, {
        method: "POST",
        body: audioBlob,
      });

      if (!result.ok) {
        throw new Error("Failed to process audio");
      }

      return (await result.json()) as ProcessOutput;
    }),
});
