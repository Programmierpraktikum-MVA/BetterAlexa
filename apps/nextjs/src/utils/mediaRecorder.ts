export const createMediaRecorder = ({
  processAudio,
  stream,
}: {
  processAudio: (audioBlob: Blob) => Promise<void>;
  stream: MediaStream;
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

  return recorder;
};
