import { useEffect, useState } from "react";

type Theme = "light" | "dark";

function useDarkMode() {
  const [theme, setTheme] = useState<Theme>("light");
  const colorTheme: Theme = theme === "dark" ? "light" : "dark";

  useEffect(() => {
    const root = window.document.documentElement;

    root.classList.remove(colorTheme);
    root.classList.add(theme);

    if (typeof window !== "undefined") {
      localStorage.setItem("theme", theme);
    }
  }, [theme, colorTheme]);

  return [colorTheme, setTheme] as const;
}

export default useDarkMode;
