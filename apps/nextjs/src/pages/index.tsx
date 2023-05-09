import { useState } from "react";
import type { NextPage } from "next";
import Head from "next/head";

import {
  GoogleAuthProvider,
  auth,
  signInWithPopup,
  useSession,
} from "@acme/auth";

import { api } from "~/utils/api";
import { blobToBase64 } from "~/utils/blobToBase64";
import { createMediaRecorder } from "~/utils/mediaRecorder";
import { MicrophoneIcon } from "~/components/MicrophoneIcon";

const Home: NextPage = () => {
  const session = useSession();
  return (
    <>
      <Head>
        <title>Better Alexa</title>
        <meta name="description" content="Generated by create-t3-app" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="flex h-screen flex-col items-center bg-gradient-to-b from-[#2e026d] to-[#15162c] text-white">
        <div className="container mt-12 flex flex-col items-center justify-center gap-4 px-4 py-8">
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-[5rem]">
            Better <span className="text-pink-400">Alexa</span>
          </h1>
          <div>
            <button
              className="rounded-lg bg-gray-700 px-3 py-2 text-sm font-semibold text-white hover:bg-gray-800"
              onClick={() => {
                if (session.user) {
                  void auth.signOut();
                  return;
                }
                const provider = new GoogleAuthProvider();
                void signInWithPopup(auth, provider);
              }}
            >
              {!session.user ? "Sign in" : "Sign out"}
            </button>
            {session.user && (
              <span className="ml-2 text-sm font-semibold text-gray-400">
                {session.user.email}
              </span>
            )}
          </div>
          {session.user && <Hidden />}
        </div>
      </main>
    </>
  );
};

const Hidden = () => {
  const [recorder, setRecorder] = useState<MediaRecorder | null>(null);
  const { mutateAsync: speechToText, isLoading: processingSpeech } =
    api.microservice.speechToText.useMutation();
  const { mutateAsync: callToAction, isLoading: processingAction } =
    api.microservice.callToAction.useMutation();
  const { mutateAsync: textToSpeech, isLoading: processingText } =
    api.microservice.textToSpeech.useMutation();
  const [text, setText] = useState("");
  const [result, setResult] = useState("");

  return (
    <div>
      <div className="flex items-center gap-1">
        <input
          value={processingSpeech || !!recorder ? "Loading..." : text}
          onChange={(e) => setText(e.target.value)}
          type="text"
          className="block w-96 rounded-md border-0 px-2 py-1 text-gray-900 shadow-sm placeholder:text-gray-400 sm:text-sm sm:leading-6"
          disabled={processingSpeech || !!recorder}
          placeholder="Alexa, play some music"
        />

        {recorder?.state !== "recording" && (
          <button
            className="aspect-square rounded-full bg-gray-700 p-2 text-sm font-semibold text-white hover:bg-gray-800 disabled:bg-gray-500"
            // eslint-disable-next-line @typescript-eslint/no-misused-promises
            onClick={async () => {
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
            }}
            disabled={processingSpeech}
          >
            <MicrophoneIcon className="h-4 w-4" />
          </button>
        )}
        {recorder?.state === "recording" && (
          <button
            className="aspect-square rounded-full bg-red-700 p-2 text-sm font-semibold text-white hover:bg-red-800 disabled:bg-red-500"
            onClick={() => {
              recorder.stop();
            }}
          >
            <MicrophoneIcon className="h-4 w-4" />
          </button>
        )}
        <button
          className="rounded-lg bg-gray-700 px-3 py-2 text-sm font-semibold text-white hover:bg-gray-800"
          // eslint-disable-next-line @typescript-eslint/no-misused-promises
          onClick={async () => {
            const data = await callToAction(text);
            setResult(data.result.text);
          }}
          disabled={processingAction}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="h-4 w-4"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
            />
          </svg>
        </button>
      </div>
      <div className="mt-4">
        {!!(result || processingAction) && (
          <pre className="max-w-[464px] whitespace-pre-wrap break-normal text-sm text-gray-400">
            {processingAction ? "Loading..." : result}
            {!processingAction && (
              <button
                // eslint-disable-next-line @typescript-eslint/no-misused-promises
                onClick={async () => {
                  const data = await textToSpeech(result);
                  const audioBlob = Buffer.from(data.result.base64, "base64");
                  const audioUrl = URL.createObjectURL(
                    new Blob([audioBlob], { type: "audio/webm" }),
                  );
                  const audio = new Audio(audioUrl);
                  void audio.play();
                }}
                disabled={processingText}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="ml-1 inline-flex h-4 w-4 self-center"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z"
                  />
                </svg>
              </button>
            )}
          </pre>
        )}
      </div>
    </div>
  );
};

export default Home;
