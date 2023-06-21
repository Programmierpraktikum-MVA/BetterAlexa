import { useEffect, type ReactNode } from "react";

import { useSession } from "@acme/auth/src/useSession";

const RouteGuard = ({ children }: { children: ReactNode }) => {
  const session = useSession();

  useEffect(() => {
    if (!session.loading && !session.user) {
      window.location.href = "/login";
    }
  }, [session]);

  return <>{children}</>;
};

export default RouteGuard;
