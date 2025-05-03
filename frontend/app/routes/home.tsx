import type { Route } from "./+types/home";
import ChatUI from "~/components/chat";
import LoginPage from "~/components/login";
import TripPage from "~/components/trip";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}

export default function Home() {
  return (
    <>
      <TripPage />
    </>
  );
}
