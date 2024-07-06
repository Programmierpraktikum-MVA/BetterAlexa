export const createMediaRecorder = ({
  processAudio,
  stream,
  timeout = 30_000,
}: {
  processAudio: (audioBlob: Blob) => Promise<void>;
  stream: MediaStream;
  timeout?: number;
}) => {
  const audioChunks: Blob[] = [];
  const recorder = new MediaRecorder(stream);

  recorder.addEventListener("dataavailable", (event: BlobEvent) => {
    audioChunks.push(event.data);
  });
  recorder.addEventListener("stop", () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    void processAudio(audioBlob).catch(console.error);
  });

  // Set a timeout to stop the recording after the specified time
  let timer: ReturnType<typeof setTimeout>;
  recorder.addEventListener("start", () => {
    timer = setTimeout(() => {
      recorder.stop();
    }, timeout);
  });
  // Clear the timeout if the recording is manually stopped before the timeout
  recorder.addEventListener("stop", () => {
    clearTimeout(timer);
  });

  return recorder;
};
