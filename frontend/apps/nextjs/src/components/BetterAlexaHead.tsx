import Head from "next/head"

export default function BetterAlexaHead() {
  return <>
    <Head>
      <title>BetterAlexa</title>
      <meta
        name="description"
        content="BetterAlexa - OpenAI with Langchain Integration"
      />
      <link
        rel="apple-touch-icon"
        sizes="180x180"
        href="/apple-touch-icon.png"
      />
      <link
        rel="icon"
        type="image/png"
        sizes="32x32"
        href="/favicon-32x32.png"
      />
      <link
        rel="icon"
        type="image/png"
        sizes="16x16"
        href="/favicon-16x16.png"
      />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <meta name="theme-color" content="#0891b2" />
      <link rel="manifest" href="/site.webmanifest" />
    </Head>
  </>
}