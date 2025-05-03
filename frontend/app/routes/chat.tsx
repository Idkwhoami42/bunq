import { useLocation, useNavigation } from "react-router";
import { toast } from "sonner";
import ChatUI from "~/components/chat";
import type { TripT } from "~/types";

export default function Chat() {
  const navigation = useNavigation();
  const state = useLocation().state as { trip: TripT } | null;

  if (!state || !state.trip) {
    toast.error("Trip not found. Please log in again.");
    navigation.navigate("/");
  }

  return <>Trip data: {JSON.stringify(state.trip)}</>;
}
