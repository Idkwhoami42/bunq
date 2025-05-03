import type { Message, TripT } from "~/types";
import type { Route } from "./+types/trip";
import SavingsPotTracker from "~/components/pot";
import { samplePot } from "~/sample_data/pot";
import LeaderboardSection from "~/components/leaderboard";

export async function loader({ params }: Route.LoaderArgs) {
  const tripId = params.id;
  const response = await fetch(`http://localhost:3000/trip/${tripId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    return null;
  }

  const data = (await response.json()) as TripT;

  if (!data.started) {
    return null;
  }

  return data;
}

export default function Pot({ loaderData }: Route.ComponentProps) {
  const trip = loaderData;

  return <LeaderboardSection pot={trip?.pot ?? samplePot} />;
}
