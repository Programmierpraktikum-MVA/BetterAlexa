import { useEffect, useState } from "react";

type Theme = "light" | "dark";

function useDarkMode(): [Theme | undefined, (theme: Theme) => void] {
  const [theme, setTheme] = useState<Theme>();
  useEffect(() => {
    const currentTheme = window.localStorage.getItem("theme");
    if (currentTheme !== null && currentTheme !== "undefined") {
      setTheme(currentTheme as Theme);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem("theme", theme as Theme);
  }, [theme]);

  return [theme, setTheme];
}

export default useDarkMode;
