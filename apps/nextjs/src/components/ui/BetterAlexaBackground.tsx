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
      {colorTheme === "light" ||
      colorTheme === undefined ||
      colorTheme === null ? (
        <main className="inset-0 flex h-screen min-h-[600px] flex-col items-center overflow-y-scroll bg-blue-500 font-['Helvetica'] text-sm text-white/100 transition-colors duration-1000">
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
        <main className="inset-0 flex h-screen min-h-[600px] flex-col items-center overflow-y-scroll bg-gray-900 font-['Helvetica'] text-sm text-white/100 transition-colors duration-1000">
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
