/** @type {import("@babel/core").ConfigFunction} */
module.exports = function (api) {
  api.cache.forever();

  // Make Expo Router run from `src/app` instead of `app`.
  // Path is relative to `/node_modules/expo-router`
  process.env.EXPO_ROUTER_APP_ROOT = "../../apps/expo/src/app";

  return {
    presets: ["babel-preset-expo"],
    plugins: [
      "nativewind/babel",
      "expo-router/babel",
      ["module-resolver", { alias: { "~": "./src" } }],
      [
        "transform-inline-environment-variables",
        {
          include: [
            "NODE_ENV",
            "ANDROID_GOOGLE_CLIENT_ID",
            "IOS_GOOGLE_CLIENT_ID",
            "EXPO_GOOGLE_CLIENT_ID",
            "NEXT_PUBLIC_API_KEY",
            "NEXT_PUBLIC_AUTH_DOMAIN",
            "NEXT_PUBLIC_PROJECT_ID",
            "NEXT_PUBLIC_STORAGE_BUCKET",
            "NEXT_PUBLIC_MESSAGING_SENDER_ID",
            "NEXT_PUBLIC_APP_ID",
          ],
        },
      ],
    ],
  };
};
