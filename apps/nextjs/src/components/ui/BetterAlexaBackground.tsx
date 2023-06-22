import { type ReactNode } from "react";

export default function BetterAlexaBackground({children} : { children: ReactNode }) {
  return <>
    <main className="flex h-screen flex-col items-center bg-gradient-to-b from-cyan-600 from-0% via-blue-500 via-35% to-blue-950 to-100% font-['Helvetica'] text-sm text-white/70">
      {children}
    </main>
  </>
}