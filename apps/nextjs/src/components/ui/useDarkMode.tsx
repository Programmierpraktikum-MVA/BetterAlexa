import { useEffect, useState } from "react";

type Theme = "light" | "dark"| null;

function useDarkMode() {
  const [theme,setTheme] = useState<Theme>();
  useEffect(() => {
    const currentTheme = window.localStorage.getItem("theme");
    if(currentTheme !== null && currentTheme !== "undefined" ){
      setTheme(currentTheme);
    }
  },[]);

  useEffect(() => {
    window.localStorage.setItem("theme", theme );
  }, [theme]);

  return [theme, setTheme];
}

export default useDarkMode;


