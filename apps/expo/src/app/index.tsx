import React, { useEffect } from "react";
import { Button, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import * as Google from "expo-auth-session/providers/google";
import { Stack } from "expo-router";
import * as WebBrowser from "expo-web-browser";

import {
  GoogleAuthProvider,
  auth,
  signInWithCredential,
  useSession,
} from "@acme/auth";

import { api } from "~/utils/api";

WebBrowser.maybeCompleteAuthSession();

const Index = () => {
  const session = useSession();
  const [request, response, promptAsync] = Google.useAuthRequest({
    androidClientId: process.env.ANDROID_GOOGLE_CLIENT_ID,
    iosClientId: process.env.IOS_GOOGLE_CLIENT_ID,
    expoClientId: process.env.EXPO_GOOGLE_CLIENT_ID,
  });

  useEffect(() => {
    if (response?.type === "success") {
      const { authentication } = response;
      const credential = GoogleAuthProvider.credential(
        authentication?.idToken,
        authentication?.accessToken,
      );
      void signInWithCredential(auth, credential);
    }
  }, [response]);

  return (
    <SafeAreaView className="bg-[#1F104A]">
      {/* Changes page title visible on the header */}
      <Stack.Screen options={{ title: "Home Page" }} />
      <View className="h-full w-full p-4">
        <Text className="mx-auto pb-2 text-5xl font-bold text-white">
          Create <Text className="text-pink-400">T3</Text> Turbo
        </Text>

        {session.user && (
          <Text className="text-white">Welcome, {session.user?.email}</Text>
        )}

        {!session.user && (
          <Button
            disabled={!request}
            onPress={() => void promptAsync()}
            title="Sign in"
            color={"#f472b6"}
          />
        )}

        {session.user && (
          <View>
            <Hidden />
            <Button
              onPress={() => void auth.signOut()}
              title="Sign out"
              color={"#f472b6"}
            />
          </View>
        )}
      </View>
    </SafeAreaView>
  );
};

const Hidden = () => {
  const { data, isLoading } = api.auth.getSecretMessage.useQuery();

  return (
    <View>
      <Text className="text-xl text-white">Secret:</Text>
      <Text className="text-white">
        {isLoading ? "Loading..." : data ?? "error"}
      </Text>
    </View>
  );
};

export default Index;
