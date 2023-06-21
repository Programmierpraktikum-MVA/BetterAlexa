import { useState } from "react";
import type { NextPage } from "next";

import {
  GoogleAuthProvider,
  auth,
  signInWithPopup,
  useSession,
} from "@acme/auth";

import { api } from "~/utils/api";
import { blobToBase64 } from "~/utils/blobToBase64";
import { createMediaRecorder } from "~/utils/mediaRecorder";
import BetterAlexaHead from "~/components/BetterAlexaHead";
import RouteGuard from "~/components/RouteGuard";
import { AudioIcon } from "~/components/ui/icons/AudioIcon";
import { MicrophoneIcon } from "~/components/ui/icons/MicrophoneIcon";
import { SendIcon } from "~/components/ui/icons/SendIcon";

const Home: NextPage = () => {
  const session = useSession();

  const logOut = async () => {
    await auth.signOut();
    window.location.href = "/login";
  };

  return (
    <>
      <BetterAlexaHead />
      <RouteGuard>
        <main className="flex h-screen flex-col items-center bg-gradient-to-b from-cyan-600 from-0% via-blue-500 via-35% to-blue-950 to-100% font-['Helvetica'] text-sm text-white/70">
          <h1 className="mt-16 text-5xl font-extrabold tracking-tight sm:text-[5rem]">
            Better<span className="text-blue-800">Alexa</span>
          </h1>
          {session.loading && <div>Loading...</div>}
          {!session.loading && (
            <>
              <div>
                <div className="fixed right-0 top-0 flex h-16 items-center">
                  {session.user && <span>{session.user.email}</span>}

                  <button
                    className="mx-5 rounded-3xl bg-black/30 px-4 py-2 backdrop-blur-xl hover:bg-black/40"
                    onClick={logOut}
                  >
                    <p>Sign out</p>
                  </button>
                </div>
              </div>
              {session.user && <Hidden />}
            </>
          )}
        </main>
      </RouteGuard>
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
    <div>
      <div className="my-8 flex items-center gap-1">
        <input
          value={processingSpeech || !!recorder ? "Loading..." : text}
          onChange={(e) => setText(e.target.value)}
          type="text"
          className="block w-full min-w-[16rem] rounded-2xl bg-black/30 px-4 py-1 leading-6 backdrop-blur-xl duration-200 placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-white sm:w-96"
          disabled={processingSpeech || !!recorder}
          placeholder="Alexa, play some music"
        />

        {recorder?.state !== "recording" && (
          <button
            className="aspect-square rounded-full bg-black/30 bg-white p-2 text-sm font-semibold backdrop-blur-xl duration-200 hover:bg-black/40 disabled:bg-black/40"
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
            className="aspect-square rounded-full bg-red-500 p-2 text-sm font-semibold text-white duration-200 hover:bg-red-600 disabled:bg-red-600"
            onClick={() => {
              recorder.stop();
            }}
          >
            <MicrophoneIcon className="h-4 w-4 stroke-gray-500" />
          </button>
        )}
        <button
          className="cursor-pointer rounded-full bg-black/30 bg-white p-2 text-sm font-semibold backdrop-blur-xl duration-200 hover:bg-black/40 disabled:bg-black/30"
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
            <div className="block w-full rounded-2xl bg-black/30 pr-2 backdrop-blur-xl">
              <div className="max-h-96 overflow-auto px-4 py-3">
                <pre className="whitespace-pre-wrap font-['Helvetica'] text-sm">
                  {processingAction ? "Loading..." : result}
                </pre>
              </div>
            </div>
            {!processingAction && (
              <button
                className="aspect-square rounded-full bg-black/30 bg-white p-2 font-semibold text-white/70 backdrop-blur-xl hover:bg-black/40 disabled:bg-black/40"
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
