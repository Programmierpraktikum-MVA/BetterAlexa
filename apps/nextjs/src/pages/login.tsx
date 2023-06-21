import { useEffect } from "react";
import type { NextPage } from "next";

import {
  GoogleAuthProvider,
  auth,
  signInWithPopup,
  useSession,
} from "@acme/auth";

import BetterAlexaHead from "~/components/BetterAlexaHead";

const Login: NextPage = () => {
  const session = useSession();

  // Redirect to index if already logged in
  useEffect(() => {
    if (session.user) {
      window.location.href = "/";
    }
  }, [session]);

  const logIn = async () => {
    if (session.user) return;

    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(auth, provider);
    
    if (result.user) {
      window.location.href = "/";
    }
  };

  return (
    <>
      <BetterAlexaHead />
      <main className="flex h-screen flex-col items-center bg-gradient-to-b from-cyan-600 from-0% via-blue-500 via-35% to-blue-950 to-100% font-['Helvetica'] text-sm text-white/70">
        <h1 className="mt-16 text-5xl font-extrabold tracking-tight sm:text-[5rem]">
          Better<span className="text-blue-800">Alexa</span>
        </h1>
        {session.loading && <div>Loading...</div>}
        {!session.loading && (
          <>
            <button
              className="mt mx-5 rounded-3xl bg-black/30 px-4 py-2 backdrop-blur-xl hover:bg-black/40"
              onClick={logIn}
            >
              Login
            </button>
          </>
        )}
      </main>
    </>
  );
};

export default Login;
