import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

import { api } from "~/utils/api";
import { blobToBase64 } from "~/utils/blobToBase64";
import { createMediaRecorder } from "~/utils/mediaRecorder";
import { AudioIcon } from "~/components/ui/icons/AudioIcon";
import { MicrophoneIcon } from "~/components/ui/icons/MicrophoneIcon";
import { SendIcon } from "~/components/ui/icons/SendIcon";
import LoadingSpinner from "./ui/LoadingSpinner";
import "katex/dist/katex.min.css";

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
  className,
}: {
  setText: (text: string) => void;
  setRecording: (recording: boolean) => void;
  className?: string;
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
    <div className={className ?? ""}>
      {recorder?.state !== "recording" && (
        <button
          className="aspect-square rounded-full bg-white p-2 text-sm font-semibold backdrop-blur-xl duration-200 hover:bg-white/40 disabled:bg-black/40 dark:bg-white/20 dark:hover:bg-white/40"
          // eslint-disable-next-line @typescript-eslint/no-misused-promises
          onClick={startRecording}
          disabled={processingSpeech}
        >
          <MicrophoneIcon className="h-4 w-4 stroke-gray-500 dark:stroke-white" />
        </button>
      )}
      {recorder?.state === "recording" && (
        <button
          className="aspect-square rounded-full bg-red-500 p-2 text-sm font-semibold text-white duration-200 hover:bg-red-600 disabled:bg-red-600"
          onClick={stopRecording}
        >
          <MicrophoneIcon className="stroke-white-500 h-4 w-4" />
        </button>
      )}
    </div>
  );
};

const ChatHistory = ({
  chatHistory,
  processingAction,
  onPlayAudioClicked,  // Add this prop
}: {
  chatHistory: ChatHistoryModel;
  processingAction: boolean;
  onPlayAudioClicked: () => void;  // Define the type for the prop
}) => {
  const { mutateAsync: textToSpeech, isLoading: processingTextToSpeech } =
    api.microservice.textToSpeech.useMutation();

  const scrollRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [scrollRef, chatHistory]);

  return (
    <>
      <div
        ref={scrollRef}
        className={`${
          chatHistory.messages.length > 0
            ? "visible max-h-[61vh]"
            : "invisible h-0"
        } chathistory-scrollbar dark:chathistory-scrollbarDark overflow-y-scroll pr-4 transition-[height] duration-500`}
      >
        {chatHistory.messages.map((message, index) => (
          <React.Fragment key={message.id || index}>
            <div className="my-4">
              {!message.fromSelf && (
                <div className="flex">
                  <div className="inline-block max-w-[70%] rounded-xl border border-slate-800 bg-slate-700 p-2">
                    <span className="break-words text-white">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath, rehypeKatex]}
                      >
                        {message.text}
                      </ReactMarkdown>
                    </span>
                  </div>
                  {index === chatHistory.messages.length - 1 && (
                    <>
                      <AudioIcon
                        className="ms-4 w-8 hover:text-blue-800 dark:hover:text-gray-400"
                        onClick={onPlayAudioClicked}
                      />
                      {processingTextToSpeech && <LoadingSpinner />}
                    </>
                  )}
                </div>
              )}

              {message.fromSelf && (
                <div className="flex flex-col items-end">
                  <div className="inline-block max-w-[70%] rounded-xl border border-slate-700 bg-slate-600 p-2">
                    <span className="break-words text-white">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath, rehypeKatex]}
                      >
                        {message.text}
                      </ReactMarkdown>
                    </span>
                  </div>
                </div>
              )}
            </div>
          </React.Fragment>
        ))}
        {processingAction && (
          <div className="my-1">
            <div className="inline-block rounded-full bg-slate-700 px-4 py-2">
              <LoadingSpinner />
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
    messages: [],
  });

  const pushMessage = (message: ChatMessageModel) => {
    setChatHistory((prev) => ({
      messages: [...prev.messages, message],
    }));
  };

  const sendCommand = async () => {
    if (text === "" || processingAction) return;
    pushMessage({
      text: text,
      fromSelf: true,
    });
    setText("");
    try {
      const data = await commandToAction(text);
      if (data.result.qdrant !== "") {
        pushMessage({
          text: data.result.qdrant,
          fromSelf: false,
        });
      }
      pushMessage({
        text: data.result.text,
        fromSelf: false,
      });
    } catch (error) {
      console.error("Failed to send command:", error);
      // Handle the error, e.g., show a user-friendly message
    }
  };

  const handleKeyPress = (event: KeyboardEvent) => {
    if (event.key === "Enter" && text !== "" && event.shiftKey === false) {
      event.preventDefault();
      sendCommand();
    }
  };

  const onPlayAudioClicked = () => {
    const lastMessage = chatHistory.messages[chatHistory.messages.length - 1]?.text;

    if (!lastMessage || lastMessage === "") return;

    void playTextToSpeech(lastMessage);
  };

  const playTextToSpeech = async (text: string) => {
    const { mutateAsync: textToSpeech, isLoading: processingTextToSpeech } =
    api.microservice.textToSpeech.useMutation();
    const data = await textToSpeech(text);
    const audioBlob = Buffer.from(data.result.base64, "base64");
    const audioUrl = URL.createObjectURL(
      new Blob([audioBlob], { type: "audio/webm" }),
    );
    const audio = new Audio(audioUrl);
    void audio.play();
  };

  return (
    <div className="flex flex-col px-4 pt-8 max-md:w-full md:w-3/4 lg:max-w-3xl">
      <div className="rounded-xl bg-gray-800/30 p-4 dark:bg-gray-700/30">
        <ChatHistory
          chatHistory={chatHistory}
          processingAction={processingAction}
          onPlayAudioClicked={onPlayAudioClicked} // Pass the function as a prop
        />

        <div className="mt-8 flex w-full items-center justify-center gap-1">
          <textarea
            value={isRecording ? "Recording..." : text}
            onChange={(e) => setText(e.target.value)}
            className="inputscroll block w-full min-w-[14rem] resize-none rounded-2xl bg-black/30 px-4 py-1 leading-6 backdrop-blur-xl transition-all duration-200 placeholder:text-white/70 focus:outline-none focus:ring-2 focus:ring-white dark:bg-white/20 sm:w-96"
            disabled={isRecording}
            placeholder="Alexa, play some music"
            onKeyDown={handleKeyPress}
          />
          <Recorder setText={setText} setRecording={setRecording} />
          <button
            className="cursor-pointer rounded-full bg-white p-2 text-sm font-semibold backdrop-blur-xl duration-200 hover:bg-white/40 dark:bg-white/20 dark:hover:bg-white/40"
            onClick={sendCommand}
            disabled={processingAction || !text}
          >
            <SendIcon className="h-4 w-6 stroke-gray-500 dark:stroke-white" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default BetterAlexaInterface;
