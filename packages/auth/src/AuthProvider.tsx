import { createContext, useEffect, useState } from "react";
import { onAuthStateChanged, signOut, type User } from "firebase/auth";

import { auth } from "./auth";

interface ISession {
  loading: boolean;
  user?: User;
}

interface IAuthProvider {
  children: React.ReactNode;
}

const init: ISession = {
  loading: true,
};

export const AuthContext = createContext<ISession>(init);

export const AuthProvider: React.FC<IAuthProvider> = ({ children }) => {
  const [session, setSession] = useState<ISession>(init);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setSession({ loading: false, user: user });
      } else {
        void signOut(auth);
        setSession({ loading: false });
      }
    });
    return unsubscribe;
  }, []);

  return (
    <AuthContext.Provider value={session}>{children}</AuthContext.Provider>
  );
};
