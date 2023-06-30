import { useEffect, useState } from "react";

import { api } from "~/utils/api";
import { blobToBase64 } from "~/utils/blobToBase64";
import { createMediaRecorder } from "~/utils/mediaRecorder";
import { AudioIcon } from "~/components/ui/icons/AudioIcon";
import { MicrophoneIcon } from "~/components/ui/icons/MicrophoneIcon";
import { SendIcon } from "~/components/ui/icons/SendIcon";
import LoadingSpinner from "./ui/LoadingSpinner";

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

const ChatHistory = ({
  chatHistory,
  processingAction,
}: {
  chatHistory: ChatHistoryModel;
  processingAction: boolean;
}) => {
  const { mutateAsync: textToSpeech, isLoading: processingTextToSpeech } =
    api.microservice.textToSpeech.useMutation();

  const playTextToSpeech = async (text: string) => {
    const data = await textToSpeech(text);
    const audioBlob = Buffer.from(data.result.base64, "base64");
    const audioUrl = URL.createObjectURL(
      new Blob([audioBlob], { type: "audio/webm" }),
    );
    const audio = new Audio(audioUrl);
    void audio.play();
  };

  const onPlayAudioClicked = () => {
    const lastMessage =
      chatHistory.messages[chatHistory.messages.length - 1]?.text;

    if (!lastMessage || lastMessage == "") return;

    void playTextToSpeech(lastMessage);
  };

  return (
    <>
      <div
        className={`${
          chatHistory.messages.length > 0 ? "visible h-[61vh]" : "invisible h-0"
        } chathistory-scrollbar overflow-y-scroll pr-4 transition-[height] duration-500`}
      >
        {chatHistory.messages.map((message, index) => (
          <>
            <div className="my-1" key={index}>
              {!message.fromSelf && (
                <div className="flex">
                  <div className="inline-block max-w-[70%] rounded-xl border border-slate-800 bg-slate-700 p-2">
                    <span className="break-words font-black text-white">
                      {message.text}
                    </span>
                  </div>
                  {chatHistory.messages.indexOf(message) ===
                    chatHistory.messages.length - 1 && (
                    <>
                      <AudioIcon
                        className="ms-4 w-8"
                        onClick={onPlayAudioClicked}
                      />

                      {processingTextToSpeech && (
                        <LoadingSpinner className="" />
                      )}
                    </>
                  )}
                </div>
              )}

              {message.fromSelf && (
                <div className="flex flex-col items-end">
                  <div className="inline-block max-w-[70%] rounded-xl border border-slate-700 bg-slate-600 p-2">
                    <span className="break-words font-black text-white">
                      {message.text}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </>
        ))}
        {processingAction && (
          <div className="my-1">
            <div className="inline-block max-w-full rounded-full bg-slate-700 p-2">
              <div className="font-black">...</div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

const BetterAlexaInterface = () => {
  const [isRecording, setRecording] = useState(false);
  const { mutateAsync: commandToAction, isLoading: processingAction } =
    api.microservice.commandToAction.useMutation();

  const [text, setText] = useState("");

  const [chatHistory, setChatHistory] = useState<ChatHistoryModel>({
    messages: [
      {
        text: "Hi, how can I help you?",
        fromSelf: false,
      },
      {
        text: "Alexa, play some music",
        fromSelf: true,
      },
      {
        text: "Playing some music",
        fromSelf: false,
      },
    ],
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
    void commandToAction(text).then((data) => {
      pushMessage({
        text: data.result.text,
        fromSelf: false,
      });
    });
  };

  return (
    <div className="flex flex-col px-2 pt-8 max-md:w-full md:w-3/4 lg:max-w-3xl">
      <div className="rounded-xl bg-[#66336699] p-4">
        <ChatHistory
          chatHistory={chatHistory}
          processingAction={processingAction}
        />

        <div className="my-8 flex w-full justify-center gap-1">
          <input
            value={isRecording ? "Recording..." : text}
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
    </div>
  );
};

export default BetterAlexaInterface;
