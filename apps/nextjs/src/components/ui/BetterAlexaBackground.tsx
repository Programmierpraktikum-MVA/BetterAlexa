import { type ReactNode } from "react";
import useDarkMode from "./useDarkMode";

export default function BetterAlexaBackground({children} : { children: ReactNode }) {
  const [colorTheme, setTheme] = useDarkMode();

  return <>
      {colorTheme === "dark"? 
      (
       <main className="fixed overflow-y-scroll inset-0 h-screen bg-blue-500 transition-all duration-1000">
        <div className="flex flex-col items-center font-['Helvetica'] text-sm text-white/100">
          <div className="fixed left-0 top-0 flex h-16 items-center">
            <button className="mx-5 rounded-3xl bg-black/30 dark:bg-white/20  hover:bg-black/40 dark:hover:bg-white/40 px-4 py-2 backdrop-blur-xl" onClick={() =>  setTheme("dark")} >
              Dark mode
            </button>
          </div>
          {children}
        </div>
        </main>
        ) 
        : 
        (
        <main className="fixed overflow-y-scroll inset-0 h-screen bg-gray-900 transition-all duration-1000">
          <div className="flex flex-col items-center font-['Helvetica'] text-sm text-white/100">
            <div className="fixed left-0 top-0 flex h-16 items-center">
              <button className="mx-5 rounded-3xl bg-black/30 dark:bg-white/20  hover:bg-black/40 dark:hover:bg-white/40 px-4 py-2 backdrop-blur-xl" onClick={() =>  setTheme("light")} >
                Light mode
              </button>
            </div>
          {children}
          </div>
        </main>
        )}
   
  </>}

