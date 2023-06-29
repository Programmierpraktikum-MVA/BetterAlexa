import { useEffect, useState } from "react";

import { api } from "~/utils/api";
import { blobToBase64 } from "~/utils/blobToBase64";
import { createMediaRecorder } from "~/utils/mediaRecorder";
import { AudioIcon } from "~/components/ui/icons/AudioIcon";
import { MicrophoneIcon } from "~/components/ui/icons/MicrophoneIcon";
import { SendIcon } from "~/components/ui/icons/SendIcon";

interface ChatHistoryModel {
  messages: ChatMessageModel[];
}
interface ChatMessageModel {
  text: string;
  fromSelf: boolean;
}

const Recorder = ({
  setText,
  setRecording,
}: {
  setText: (text: string) => void;
  setRecording: (recording: boolean) => void;
}) => {
  const [recorder, setRecorder] = useState<MediaRecorder | null>(null);
  const { mutateAsync: speechToText, isLoading: processingSpeech } =
    api.microservice.speechToText.useMutation();

  useEffect(() => {
    setRecording(processingSpeech || !!recorder);
  }, [processingSpeech, recorder, setRecording]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });
    const recorder = createMediaRecorder({
      stream,
      processAudio: async (blob) => {
        const base64 = await blobToBase64(blob);
        setRecorder(null);
        const data = await speechToText(base64);
        setText(data.result.text);
      },
    });
    setRecorder(recorder);
    recorder.start();
  };

  const stopRecording = () => {
    recorder?.stop();
  };

  return (
    <>
      {recorder?.state !== "recording" && (
        <button
          className="aspect-square rounded-full bg-black/30 bg-white p-2 text-sm font-semibold backdrop-blur-xl duration-200 hover:bg-black/40 disabled:bg-black/40"
          // eslint-disable-next-line @typescript-eslint/no-misused-promises
          onClick={startRecording}
          disabled={processingSpeech}
        >
          <MicrophoneIcon className="h-4 w-4 stroke-gray-500" />
        </button>
      )}
      {recorder?.state === "recording" && (
        <button
          className="aspect-square rounded-full bg-red-500 p-2 text-sm font-semibold text-white duration-200 hover:bg-red-600 disabled:bg-red-600"
          onClick={stopRecording}
        >
          <MicrophoneIcon className="h-4 w-4 stroke-gray-500" />
        </button>
      )}
    </>
  );
};

const BetterAlexaInterface = () => {
  const [isRecording, setRecording] = useState(false);
  const { mutateAsync: commandToAction, isLoading: processingAction } =
    api.microservice.commandToAction.useMutation();
  const { mutateAsync: textToSpeech, isLoading: processingText } =
    api.microservice.textToSpeech.useMutation();
  const [text, setText] = useState("");

  const transformResultToSpeech = async (text: string) => {
    const data = await textToSpeech(text);
    const audioBlob = Buffer.from(data.result.base64, "base64");
    const audioUrl = URL.createObjectURL(
      new Blob([audioBlob], { type: "audio/webm" }),
    );
    const audio = new Audio(audioUrl);
    void audio.play();
  };

  const [chatHistory, setChatHistory] = useState<ChatHistoryModel>({
    messages: [],
  });

  const pushMessage = (message: ChatMessageModel) => {
    setChatHistory((prev) => ({
      messages: [...prev.messages, message],
    }));
  };

  const sendCommand = () => {
    pushMessage({
      text: text,
      fromSelf: true,
    });
    setText("");
    commandToAction(text)
      .then((data) => {
        pushMessage({
          text: data.result.text,
          fromSelf: false,
        });
      })
      .catch((error) => {
        //todo: show error
      });
  };

  return (
    <div className="flex flex-col max-md:w-full md:w-1/4">
      {chatHistory.messages.map((message, index) => (
        <div className="my-1" key={index}>
          <div className="w-auto bg-slate-700 p-2 font-black">
            {`${message.fromSelf ? "Me" : "AI"}: ${message.text}`}
          </div>
        </div>
      ))}
      {processingText && (
        <div className="my-1">
          <div className="w-auto bg-slate-700 p-2 font-black">asdfsadf</div>
        </div>
      )}
      <div className="my-8 flex items-center gap-1">
        <input
          value={isRecording ? "Loading..." : text}
          onChange={(e) => setText(e.target.value)}
          type="text"
          className="block w-full min-w-[16rem] rounded-2xl bg-black/30 px-4 py-1 leading-6 backdrop-blur-xl duration-200 placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-white sm:w-96"
          disabled={isRecording}
          placeholder="Alexa, play some music"
        />
        <Recorder setText={setText} setRecording={setRecording} />
        <button
          className="cursor-pointer rounded-full bg-black/30 bg-white p-2 text-sm font-semibold backdrop-blur-xl duration-200 hover:bg-black/40 disabled:bg-black/30"
          onClick={sendCommand}
          disabled={processingAction || !text}
        >
          <SendIcon className="h-4 w-6 stroke-gray-500" />
        </button>
      </div>
    </div>
  );
};

export default BetterAlexaInterface;
