
import type { NextPage } from "next";

import { auth, useSession } from "@acme/auth";


import BetterAlexaHead from "~/components/BetterAlexaHead";
import RouteGuard from "~/components/RouteGuard";
import BetterAlexaBackground from "~/components/ui/BetterAlexaBackground";
import BetterAlexaLogo from "~/components/ui/BetterAlexaLogo";
import BetterAlexaInterface from "~/components/BetterAlexaInterface";


const Home: NextPage = () => {
  const session = useSession();

  const logOut = () => {
    auth
      .signOut()
      .then(() => {
        window.location.href = "/login";
      })
      .catch((error) => {
        console.error("Error signing out: ", error);
      });
  };

  return (
    <>
      <BetterAlexaHead />

      <RouteGuard>
        <BetterAlexaBackground>
          <BetterAlexaLogo />

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
              {session.user && <BetterAlexaInterface />}
            </>
          )}
        </BetterAlexaBackground>
      </RouteGuard>
    </>
  );
};


export default Home;
