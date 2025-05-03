import { useCallback, useEffect, useState } from "react";
import type { Route } from "./+types/trip";
import { io, type Socket } from "socket.io-client";
import { useNavigate } from "react-router";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Users, ArrowRight, Loader2, Copy } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Avatar, AvatarFallback } from "~/components/ui/avatar";
import type { TripT } from "~/types";

const locationMap: Record<string, { name: string; icon: string }> = {
  beach: { name: "Beach", icon: "🏖️" },
  mountain: { name: "Mountain", icon: "🏔️" },
  city: { name: "City", icon: "🏙️" },
  countryside: { name: "Countryside", icon: "🌄" },
  island: { name: "Island", icon: "🏝️" },
};

export async function loader({
  params,
}: Route.LoaderArgs): Promise<TripT | null> {
  let tripId = params.id;
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
  return data;
}

export default function Trip({ loaderData }: Route.ComponentProps) {
  const [username, setUsername] = useState<string | null>(null);
  const [trip, setTrip] = useState<TripT | null>(loaderData);
  const [socket, setSocket] = useState<Socket | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!trip) {
      navigate("/");
      return;
    }

    if (trip.started) {
      toast.error("Trip has already started. Redirecting to chat...");
      navigate(`/trip/${trip.id}/chat`);
      return;
    }

    const storedUsername = sessionStorage.getItem("username");
    if (!storedUsername) {
      toast.error("Username not found. Please log in again.");
      navigate("/");
      return;
    }

    setUsername(storedUsername);

    const socketInstance = io("http://localhost:3000/trip", {
      transports: ["websocket"],
      autoConnect: true,
    });

    socketInstance.on("connect", () => {
      console.log("Connected to trip socket");

      socketInstance.emit("joinTrip", {
        tripId: trip.id,
        username: storedUsername,
      });
    });

    socketInstance.on("tripUpdate", (tripData: TripT) => {
      setTrip(tripData);
    });

    socketInstance.on("error", (error: string) => {
      toast.error(error);
    });

    socketInstance.on("tripStarted", (tripId: string) => {
      toast.success("Trip has started!");
      navigate(`/trip/${tripId}/chat`);
    });

    socketInstance.on("disconnect", () => {
      console.log("Disconnected from trip socket");
      navigate("/");
    });

    setSocket(socketInstance);

    return () => {};
  }, []);

  const handleStartTrip = () => {
    if (trip && socket) {
      socket.emit("startTrip", {
        tripId: trip.id,
      });
    }
  };

  if (trip === null || username === null) {
    return (
      <div className="flex min-h-[100dvh] items-center justify-center bg-gray-50 p-4">
        <Card className="w-full max-w-md">
          <CardContent>
            <p className="text-center text-lg">Loading...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getInitials = (name: string) => {
    return name.substring(0, 2).toUpperCase();
  };

  const getLocationDetails = () => {
    return { name: trip.location.name, icon: "🗺️" };
  };

  const locationDetails = getLocationDetails();

  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="pb-2">
          <CardTitle className="text-xl">
            <div className="flex justify-between items-center">
              {trip.name}
              {trip.creator === username && (
                <p className="text-xs text-gray-500">
                  Code: {trip.id}
                  <span
                    onClick={() => {
                      navigator.clipboard.writeText(trip.id);
                      toast.success("Trip code copied to clipboard!");
                    }}
                    className="ml-[1ch] cursor-pointer hover:underline"
                  >
                    <Copy className="w-4 h-4 inline-block mr-1" />
                  </span>
                </p>
              )}
            </div>
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Location Section */}
          <div className="flex items-center justify-center space-x-2 p-4 bg-gray-100 rounded-lg">
            <span className="text-3xl">{locationDetails.icon}</span>
            <div>
              <h3 className="font-medium">{locationDetails.name}</h3>
            </div>
          </div>

          {/* Participants Section */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-gray-500" />
              <h3 className="font-medium">Participants</h3>
            </div>

            <div className="space-y-2">
              {/* Current user */}
              <div className="flex items-center justify-between p-2 bg-primary/10 rounded-md">
                <div className="flex items-center space-x-3">
                  <Avatar className="h-8 w-8 bg-primary text-primary-foreground">
                    <AvatarFallback>
                      <img
                        src={`https://api.dicebear.com/9.x/adventurer/svg?seed=${username}`}
                        height={30}
                        width={30}
                      />
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-medium">{username} (You)</p>
                    {trip.creator === username && (
                      <p className="text-xs text-gray-500">Trip Creator</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Other participants */}
              {trip.users
                .filter((user) => user !== username)
                .map((user) => (
                  <div
                    key={user}
                    className="flex items-center justify-between p-2 bg-gray-100 rounded-md"
                  >
                    <div className="flex items-center space-x-3">
                      <Avatar className="h-8 w-8 bg-primary text-primary-foreground">
                        <AvatarFallback>
                          <img
                            src={`https://api.dicebear.com/9.x/adventurer/svg?seed=${user}`}
                            height={30}
                            width={30}
                          />
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{user}</p>
                        {trip.creator === user && (
                          <p className="text-xs text-gray-500">Trip Creator</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </CardContent>

        <CardFooter>
          {trip.creator === username ? (
            <Button
              onClick={handleStartTrip}
              className="w-full flex items-center justify-center space-x-2"
            >
              <span>Start Trip</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <div className="flex items-center justify-center space-x-2">
              <p className="text-sm text-gray-500">
                Waiting for the trip creator to start the trip...
              </p>
              <Loader2 className="h-4 w-4 text-gray-500 animate-spin" />
            </div>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
