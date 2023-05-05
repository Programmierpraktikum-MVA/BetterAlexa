import { getAuth } from "firebase/auth";

import { app } from "./firebase";

export { type User } from "firebase/auth";

export { signInWithPopup, GoogleAuthProvider } from "firebase/auth";

export const auth = getAuth(app);
