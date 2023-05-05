import admin from "firebase-admin";
import { type ServiceAccount } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";

import serviceAccount from "../service_account.json";

export const adminApp = !admin.apps.length
  ? admin.initializeApp({
      credential: admin.credential.cert(serviceAccount as ServiceAccount),
    })
  : admin.app();
export const adminAuth = getAuth(adminApp);
