import { useContext } from "react";

import { AuthContext } from "./AuthProvider";

export const useSession = () => useContext(AuthContext);
