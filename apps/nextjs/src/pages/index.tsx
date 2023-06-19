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
import { SendIcon } from "~/components/SendIcon";
import { AudioIcon } from "~/components/AudioIcon";

const Home: NextPage = () => {
  const session = useSession();
  return (
    <>
      <Head>
        <title>Better Alexa</title>
        <meta name="description" content="Generated by create-t3-app" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="flex h-screen flex-col items-center text-white/70 font-['Helvetica'] text-sm bg-gradient-to-b from-cyan-600 from-0% via-blue-500 via-35% to-blue-950 to-100%">
        <h1 className="mt-16 text-3xl font-bold backdrop-blur-xl">Better Alexa</h1>
        {session.loading && <div>Loading...</div>}
        {!session.loading && (
          <>
            <div>
              <div className="flex h-16 fixed items-center top-0 right-0">
                {session.user && (
                  <span>
                    {session.user.email}
                  </span>
                )}

                <button
                  className="mx-5 rounded-3xl px-4 py-2 backdrop-blur-xl bg-black/30 hover:bg-black/40"
                  onClick={() => {
                    if (session.user) {
                      void auth.signOut();
                      return;
                    }
                    const provider = new GoogleAuthProvider();
                    void signInWithPopup(auth, provider);
                  }}
                >
                  <p>{!session.user ? "Sign in" : "Sign out"}</p>
                </button>
              </div>
            </div>
            {session.user && <Hidden />}
          </>
        )}

      </main>
    </>
  );
};

const Hidden = () => {
  const [recorder, setRecorder] = useState<MediaRecorder | null>(null);
  const { mutateAsync: speechToText, isLoading: processingSpeech } =
    api.microservice.speechToText.useMutation();
  const { mutateAsync: commandToAction, isLoading: processingAction } =
    api.microservice.commandToAction.useMutation();
  const { mutateAsync: textToSpeech, isLoading: processingText } =
    api.microservice.textToSpeech.useMutation();
  const [text, setText] = useState("");
  const [result, setResult] = useState("");

  return (
    <div className="w-[500px]">
      <div className="flex items-center gap-1 my-8">
        <input
          value={processingSpeech || !!recorder ? "Loading..." : text}
          onChange={(e) => setText(e.target.value)}
          type="text"
          className="block w-full rounded-2xl focus:outline-none focus:ring-white focus:ring-2 px-4 py-1 backdrop-blur-xl bg-black/30 placeholder:text-white/30 leading-6 duration-200"
          disabled={processingSpeech || !!recorder}
          placeholder="Alexa, play some music"
        />

        {recorder?.state !== "recording" && (
          <button
            className="aspect-square rounded-full bg-white p-2 text-sm font-semibold hover:bg-black/40 disabled:bg-black/40 backdrop-blur-xl bg-black/30 duration-200"
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
            <MicrophoneIcon className="h-4 w-4 stroke-gray-500" />
          </button>
        )}
        {recorder?.state === "recording" && (
          <button
            className="aspect-square rounded-full bg-red-500 p-2 text-sm font-semibold text-white hover:bg-red-600 disabled:bg-red-600 duration-200"
            onClick={() => {
              recorder.stop();
            }}
          >
            <MicrophoneIcon className="h-4 w-4 stroke-gray-500" />
          </button>
        )}
        <button
          className="rounded-full bg-white px-3 py-2 text-sm font-semibold cursor-pointer backdrop-blur-xl bg-black/30 hover:bg-black/40 disabled:bg-black/30 duration-200"
          // eslint-disable-next-line @typescript-eslint/no-misused-promises
          onClick={async () => {
            const data = await commandToAction(text);
            setResult(data.result.text);
          }}
          disabled={processingAction || !text}
        >
          <SendIcon className="h-4 w-6 stroke-gray-500" />
        </button>
      </div>
      <div>
        {!!(result || processingAction) && (
          <div className="flex items-center gap-1">
            <div className="w-full block rounded-2xl pr-2 backdrop-blur-xl bg-black/30">
              <div className="max-h-96 px-4 py-3 overflow-auto">
                <pre className="whitespace-pre-wrap text-sm font-['Helvetica']">
                  {processingAction ? "Loading..." : result}
                </pre>
              </div>
            </div>
            {!processingAction && (
              <button
                className="aspect-square rounded-full bg-white p-2 font-semibold text-white/70 hover:bg-black/40 disabled:bg-black/40 backdrop-blur-xl bg-black/30"
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
                <AudioIcon className="h-4 w-4 stroke-gray-500" />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;

