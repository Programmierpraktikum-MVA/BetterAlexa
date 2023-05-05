import { AuthProvider } from "@acme/auth";

import "../styles/globals.css";
import type { AppType } from "next/app";

import { api } from "~/utils/api";

const MyApp: AppType = ({ Component, pageProps }) => {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
};

export default api.withTRPC(MyApp);
