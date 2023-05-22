import { AuthProvider } from "@acme/auth";

import "../styles/globals.css";
import type { AppType } from "next/app";

import { api } from "~/utils/api";
import { Toaster } from "~/components/ui/toaster";

const MyApp: AppType = ({ Component, pageProps }) => {
  return (
    <AuthProvider>
      <Component {...pageProps} />
      <Toaster />
    </AuthProvider>
  );
};

export default api.withTRPC(MyApp);
