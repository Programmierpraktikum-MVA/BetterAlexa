import { useEffect, useState } from "react";

import { api } from "~/utils/api";
import { blobToBase64 } from "~/utils/blobToBase64";
import { createMediaRecorder } from "~/utils/mediaRecorder";

const RecordAudio = () => {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [recorder, setRecorder] = useState<MediaRecorder | null>(null);
  const { mutateAsync } = api.audio.process.useMutation();

  useEffect(() => {
    void navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      setStream(stream);
    });
  }, []);

  return (
    <div className="flex flex-col items-center">
      <h1 className="mb-2 mt-8 text-2xl font-bold">Record audio</h1>
      {stream && (
        <div className="flex gap-1">
          {!recorder && (
            <button
              className="aspect-square rounded-full bg-gray-700 p-4 text-sm font-semibold text-white hover:bg-gray-800"
              onClick={() => {
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
          {recorder && (
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
      )}
      {!stream && <p>Please allow microphone to continue</p>}
    </div>
  );
};

export default RecordAudio;
