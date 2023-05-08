import { useState } from "react";

import { api } from "~/utils/api";
import { blobToBase64 } from "~/utils/blobToBase64";
import { createMediaRecorder } from "~/utils/mediaRecorder";

const RecordAudio = () => {
  const [recorder, setRecorder] = useState<MediaRecorder | null>(null);
  const { mutateAsync } = api.audio.process.useMutation();

  return (
    <div className="flex flex-col items-center">
      <h1 className="mb-2 mt-8 text-2xl font-bold">Record audio</h1>
      <div className="flex gap-1">
        {recorder?.state !== "recording" && (
          <button
            className="aspect-square rounded-full bg-gray-700 p-4 text-sm font-semibold text-white hover:bg-gray-800"
            // eslint-disable-next-line @typescript-eslint/no-misused-promises
            onClick={async () => {
              const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
              });
              const recorder = createMediaRecorder({
                stream,
                processAudio: async (blob) => {
                  const base64 = await blobToBase64(blob);
                  await mutateAsync(base64);
                },
              });
              setRecorder(recorder);
              recorder.start();
            }}
          >
            Start recording
          </button>
        )}
        {recorder?.state === "recording" && (
          <button
            className="aspect-square rounded-full border border-black bg-red-700 p-4 text-sm font-semibold text-white hover:bg-red-800"
            onClick={() => {
              recorder.stop();
              setRecorder(null);
            }}
          >
            Stop recording
          </button>
        )}
      </div>
    </div>
  );
};

export default RecordAudio;
