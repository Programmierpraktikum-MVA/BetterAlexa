import { useEffect, useState } from "react";
import { onAuthStateChanged, signOut, type User } from "firebase/auth";

import { auth } from "./auth";

export interface IUseSession {
  loading: boolean;
  user?: User;
}

const init: IUseSession = {
  loading: true,
};

export const useSession = () => {
  const [session, setSession] = useState(init);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setSession({ loading: false, user: user });
      } else {
        void signOut(auth);
        setSession({ loading: false, user: undefined });
      }
    });

    return () => unsubscribe();
  }, []);

  return session;
};
