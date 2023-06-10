import admin from "firebase-admin";
import { getAuth } from "firebase-admin/auth";

export const adminApp = () =>
  !admin.apps.length
    ? admin.initializeApp({
        credential: admin.credential.cert({
          projectId: process.env.FIREBASE_PROJECT_ID,
          clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
          privateKey: process.env.FIREBASE_PRIVATE_KEY,
        }),
      })
    : admin.app();
export const adminAuth = () => getAuth(adminApp());
