/* eslint-disable @typescript-eslint/no-misused-promises */
import React, { useEffect, useState } from "react";
import {
  Button,
  ScrollView,
  Text,
  TextInput,
  TouchableHighlight,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import * as Google from "expo-auth-session/providers/google";
import { Stack } from "expo-router";
import * as SecureStore from "expo-secure-store";
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
    Promise.all([
      SecureStore.getItemAsync("idToken"),
      SecureStore.getItemAsync("accessToken"),
    ])
      .then(([idToken, accessToken]) => {
        if (idToken && accessToken) {
          const credential = GoogleAuthProvider.credential(
            idToken,
            accessToken,
          );
          void signInWithCredential(auth, credential);
        }
      })
      .catch((err) => {
        console.error(err);
      });
  }, []);

  useEffect(() => {
    if (response?.type === "success") {
      const { authentication } = response;
      void Promise.all([
        SecureStore.setItemAsync("idToken", authentication?.idToken ?? ""),
        SecureStore.setItemAsync(
          "accessToken",
          authentication?.accessToken ?? "",
        ),
      ]);
      const credential = GoogleAuthProvider.credential(
        authentication?.idToken,
        authentication?.accessToken,
      );
      void signInWithCredential(auth, credential);
    }
  }, [response]);

  return (
    <SafeAreaView className="bg-[#150a18]">
      {/* Changes page title visible on the header */}
      <Stack.Screen options={{ title: "Index" }} />
      <View className="mt-[20vh] h-full w-full p-4">
        <Text className="mx-auto pb-2 text-5xl font-bold text-white">
          Better<Text className="text-pink-400">Alexa</Text>
        </Text>

        {session.loading && (
          <Text className="mx-auto text-white">Loading...</Text>
        )}

        {session.user && (
          <Text className="mx-auto text-white">
            Welcome, {session.user?.email}👋
          </Text>
        )}

        {!session.loading && !session.user && (
          <Button
            disabled={!request}
            onPress={() => void promptAsync()}
            title="Sign in with Google"
            color={"#f472b6"}
          />
        )}

        {session.user && (
          <View className="h-full">
            <Button
              onPress={() => {
                void auth.signOut();
                Promise.all([
                  SecureStore.deleteItemAsync("idToken"),
                  SecureStore.deleteItemAsync("accessToken"),
                ]).catch((err) => {
                  console.error(err);
                });
              }}
              title="Sign out"
              color={"#f472b6"}
            />
            <Hidden />
          </View>
        )}
      </View>
    </SafeAreaView>
  );
};

const Hidden = () => {
  const { mutateAsync: commandToAction, isLoading: processingAction } =
    api.microservice.commandToAction.useMutation();
  const [text, setText] = useState("");
  const [result, setResult] = useState("");

  return (
    <View className="mt-2">
      <View className="flex flex-row gap-1">
        <TextInput
          placeholder="Hello, Alexa!"
          className="max-h-[20vh] flex-1 rounded-md bg-white px-4 py-2"
          onChangeText={(text) => setText(text)}
          multiline
        />
        <TouchableHighlight
          className="h-8 w-8 items-center rounded-md bg-pink-500 p-2"
          onPress={async () => {
            const data = await commandToAction(text);
            setResult(data.result.text);
          }}
          disabled={processingAction || !text}
        >
          <Text className="text-white">▶</Text>
        </TouchableHighlight>
      </View>
      {!!(result || processingAction) && (
        <View className="mt-4 max-h-[30vh] rounded-md bg-black/40 p-4">
          <ScrollView>
            <Text
              className="whitespace-pre-wrap break-normal text-sm text-gray-400"
              selectable
            >
              {processingAction ? "Loading..." : result}
            </Text>
          </ScrollView>
        </View>
      )}
    </View>
  );
};

export default Index;
