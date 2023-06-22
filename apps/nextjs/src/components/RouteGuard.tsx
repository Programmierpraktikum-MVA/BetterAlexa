import { useEffect } from "react";

import { useSession } from "@acme/auth/src/useSession";

const RouteGuard = () => {
  const session = useSession();

  useEffect(() => {
    if (!session.loading && !session.user) {
      window.location.href = "/login";
    }
  }, [session]);

  return <></>;
};

export default RouteGuard;
