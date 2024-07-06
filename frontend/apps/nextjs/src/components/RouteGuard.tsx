import { useEffect } from "react";
import Router from "next/router";

import { useSession } from "@acme/auth/src/useSession";

const RouteGuard = () => {
  const session = useSession();

  useEffect(() => {
    if (!session.loading && !session.user) {
      void Router.push("/login");
    }
  }, [session]);

  return <></>;
};

export default RouteGuard;
