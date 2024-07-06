import type { ExpoConfig } from "@expo/config";

const defineConfig = (): ExpoConfig => ({
  name: "Better Alexa",
  slug: "betteralexa",
  scheme: "betteralexa",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  userInterfaceStyle: "light",
  splash: {
    image: "./assets/icon.png",
    resizeMode: "contain",
    backgroundColor: "#150a18",
  },
  updates: {
    fallbackToCacheTimeout: 0,
  },
  assetBundlePatterns: ["**/*"],
  ios: {
    supportsTablet: true,
    bundleIdentifier: "com.mva.betteralexa",
    config: {
      usesNonExemptEncryption: false,
    },
  },
  android: {
    package: "com.mva.betteralexa",
    adaptiveIcon: {
      foregroundImage: "./assets/icon.png",
      backgroundColor: "#150a18",
    },
  },
  extra: {
    eas: {
      projectId: "5f5d1e96-959f-4d6c-9603-2f5a79bea126",
    },
  },
  plugins: ["./expo-plugins/with-modify-gradle.js"],
});

export default defineConfig;
