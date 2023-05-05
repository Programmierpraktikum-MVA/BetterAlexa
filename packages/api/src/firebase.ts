import admin from "firebase-admin";
import { initializeApp, type ServiceAccount } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";

import serviceAccount from "../service_account.json";

export const adminApp = initializeApp({
  credential: admin.credential.cert(serviceAccount as ServiceAccount),
});
export const adminAuth = getAuth(adminApp);
