import { type ReactNode } from "react";

import useDarkMode from "./useDarkMode";

export default function BetterAlexaBackground({
  children,
}: {
  children: ReactNode;
}) {
  const [colorTheme, setTheme] = useDarkMode();

  return (
    <>
      {colorTheme === "dark" ? (
        <main className="flex h-screen flex-col items-center bg-blue-500 font-['Helvetica'] text-sm text-white/100 transition-all duration-1000">
          <div className="fixed left-0 top-0 flex h-16 items-center">
            <button
              className="mx-5 h-8 w-8 rounded-3xl bg-black/30 backdrop-blur-xl hover:bg-black/40 dark:bg-white/20 dark:hover:bg-white/40"
              onClick={() => setTheme("dark")}
            >
              ☽
            </button>
          </div>
          {children}
        </main>
      ) : (
        <main className="flex h-screen flex-col items-center bg-gray-900 font-['Helvetica'] text-sm text-white/100 transition-all duration-1000">
          <div className="fixed left-0 top-0 flex h-16 items-center">
            <button
              className="mx-5 h-8 w-8 rounded-3xl bg-black/30 backdrop-blur-xl hover:bg-black/40 dark:bg-white/20 dark:hover:bg-white/40"
              onClick={() => setTheme("light")}
            >
              ☀️
            </button>
          </div>
          {children}
        </main>
      )}
    </>
  );
}
