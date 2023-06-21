import { useEffect, useState } from "react";
import type { NextPage } from "next";

import {
  GoogleAuthProvider,
  auth,
  signInWithPopup,
  useSession,
} from "@acme/auth";

import BetterAlexaHead from "~/components/BetterAlexaHead";
import BetterAlexaBackground from "~/components/ui/BetterAlexaBackground";
import BetterAlexaLogo from "~/components/ui/BetterAlexaLogo";

const Login: NextPage = () => {
  const session = useSession();

  // Redirect to index if already logged in
  useEffect(() => {
    if (session.user) {
      window.location.href = "/";
    }
  }, [session]);

  const logIn = () => {
    if (session.user) {
      window.location.href = "/";
      return;
    }

    const provider = new GoogleAuthProvider();
    signInWithPopup(auth, provider)
      .then((result) => {
        if (result.user) window.location.href = "/";
      })
      .catch((_) => {
        console.error("Error signing in");
      });
  };

  return (
    <>
      <BetterAlexaHead />

      <BetterAlexaBackground>
        <BetterAlexaLogo />

        {session.loading && <div>Loading...</div>}
        {!session.loading && (
          <>
            <button
              className="mx-5 mt-16 rounded-3xl bg-black/30 px-4 py-2 backdrop-blur-xl hover:bg-black/40"
              onClick={logIn}
            >
              Login
            </button>
          </>
        )}
      </BetterAlexaBackground>
    </>
  );
};

export default Login;
