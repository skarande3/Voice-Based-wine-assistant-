import { createBrowserRouter } from "react-router";
import WelcomeScreen from "./screens/WelcomeScreen";
import TransitionScreen from "./screens/TransitionScreen";
import VoiceInterface from "./screens/VoiceInterface";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: WelcomeScreen,
  },
  {
    path: "/intro",
    Component: TransitionScreen,
  },
  {
    path: "/assistant",
    Component: VoiceInterface,
  },
]);
