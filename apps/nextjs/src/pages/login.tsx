import { useEffect } from "react";
import type { NextPage } from "next";
import Router from "next/router";

import {
  GoogleAuthProvider,
  auth,
  signInWithRedirect,
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
      void Router.push("/");
    }
  }, [session]);

  const logIn = () => {
    const provider = new GoogleAuthProvider();
    void signInWithRedirect(auth, provider);
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
