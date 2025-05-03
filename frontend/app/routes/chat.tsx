import type { Locations, Message, TripT } from "~/types";
import type { Route } from "./+types/trip";
import { useEffect, useRef, useState } from "react";
import { io, type Socket } from "socket.io-client";
import { useNavigate } from "react-router";
import { toast } from "sonner";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { Card } from "~/components/ui/card";
import {
  CircleX,
  MapPin,
  PieChart,
  Send,
  Share,
  Share2,
  Trophy,
  Users,
} from "lucide-react";
import { Avatar } from "@radix-ui/react-avatar";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Badge } from "~/components/ui/badge";
import ReactMarkdown from "react-markdown";
import GoogleEarthViewer from "~/components/earth";

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

export default function Chat({ loaderData }: Route.ComponentProps) {
  const [trip, setTrip] = useState<TripT | null>(loaderData);
  const [socket, setSocket] = useState<Socket | null>(null);
  const navigate = useNavigate();
  const [message, setMessage] = useState<string>("");
  const [username, setUsername] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [typing, setTyping] = useState(false);
  const [userTyping, setUserTyping] = useState<string | null>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!trip) return;

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
      console.log("Trip updated:", tripData);
      setTrip(tripData);
    });

    socketInstance.on("disconnect", () => {
      console.log("Disconnected from trip socket");
      toast.error("Disconnected from trip socket. Please refresh the page.");
      navigate("/");
    });

    socketInstance.on("userTyping", ({ username }: { username: string }) => {
      if (username !== storedUsername) {
        setUserTyping(username);
      }
    });

    socketInstance.on(
      "userStoppedTyping",
      ({ username }: { username: string }) => {
        if (username !== storedUsername) {
          setUserTyping(null);
        }
      }
    );

    setSocket(socketInstance);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [trip?.chat.messages]);

  if (!trip || !trip.started || !username) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  const formatTime = (timestamp: Date) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!socket || !message.trim()) return;

    const messageData = {
      username,
      tripId: trip.id,
      message,
    };

    socket.emit("message", messageData);
    setMessage("");
    setTyping(false);
    socket.emit("userstoppedtyping", { tripId: trip.id, username });
  };

  const isCurrentUser = (sender: string) => sender === username;

  const handleTyping = () => {
    if (!socket) return;

    if (!typing) {
      setTyping(true);
      socket.emit("usertyping", { tripId: trip.id, username });
    }

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    typingTimeoutRef.current = setTimeout(() => {
      setTyping(false);
      socket.emit("userstoppedtyping", { tripId: trip.id, username });
    }, 1000);
  };

  return (
    <div className="flex flex-col h-screen max-h-screen bg-muted/30">
      {/* Header */}
      <div className="bg-background border-b p-4 shadow-sm">
        <div className="container mx-auto max-w-4xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold">{trip.name}</h1>
                <Badge variant="outline" className="flex items-center gap-1">
                  <Users size={14} />
                  <span>{trip.users.length}</span>
                </Badge>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground mt-1">
                <MapPin size={16} />
                <span>{trip.location.name}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  navigator.clipboard.writeText(trip.id);
                  toast.success("Trip ID copied to clipboard!");
                }}
              >
                <Share2 size={14} className="mr-2" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate(`/trip/${trip.id}/pot`)}
                disabled={trip.pot === undefined}
              >
                <PieChart size={14} className="mr-2" />
                Pot
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate(`/trip/${trip.id}/leaderboard`)}
                disabled={trip.pot === undefined}
              >
                <Trophy size={14} className="mr-2" />
                Leaderboard
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden container mx-auto max-w-4xl py-4 px-4">
        <Card className="h-full flex flex-col">
          <ScrollArea className="flex-1 p-4 overflow-auto">
            <div className="space-y-1">
              {trip.chat.messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  <p>No messages yet. Start the conversation!</p>
                </div>
              ) : (
                trip.chat.messages.map((msg, index) => (
                  <ChatMessage
                    key={index}
                    message={msg}
                    isCurrentUser={isCurrentUser(msg.sender)}
                    formatTime={formatTime}
                    locations={trip.locations}
                    messageRef={messagesEndRef}
                  />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
          {userTyping && (
            <div className="p-2 text-sm text-muted-foreground italic">
              {userTyping} is typing...
            </div>
          )}

          {/* Message Input */}
          <form onSubmit={handleSubmit} className="px-2 flex-0">
            <div className="flex gap-2">
              <Input
                value={message}
                onChange={(e) => {
                  setMessage(e.target.value);
                  handleTyping();
                }}
                placeholder="Type your message..."
                className="flex-1"
                autoComplete="off"
              />
              <Button type="submit" disabled={!message.trim()}>
                <Send size={18} />
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}

interface ChatMessageProps {
  message: Message;
  isCurrentUser: boolean;
  formatTime: (timestamp: Date) => string;
  locations: Locations[][];
  messageRef: React.RefObject<HTMLDivElement | null>;
}

function ChatMessage({
  message: msg,
  isCurrentUser,
  formatTime,
  locations,
  messageRef,
}: ChatMessageProps) {
  const [location, setLocation] = useState<Locations | null>(null);
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // When location changes, scroll to the map or back to the message
    if (ref.current) {
      setTimeout(() => {
        ref.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
  }, [location]);

  return (
    <div
      className={`flex my-2 ${isCurrentUser ? "justify-end" : "justify-start"}`}
    >
      <div className={`max-w-[80%] ${isCurrentUser ? "order-2" : "order-1"}`}>
        {!isCurrentUser && (
          <div className="text-lg font-medium ml-1">{msg.sender}</div>
        )}
        <div className="flex items-end gap-1">
          <div
            className={`rounded-lg px-2 ${
              isCurrentUser
                ? "bg-primary text-primary-foreground"
                : msg.sender === "AI"
                ? "bg-gray-400"
                : "bg-muted"
            }`}
          >
            <div className="markdown m-0">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
            <div
              className={`text-xs ${
                isCurrentUser
                  ? "text-primary-foreground/70"
                  : "text-muted-foreground"
              }`}
            >
              {formatTime(msg.timestamp)}
            </div>
          </div>
          {msg.locationIndex !== undefined && (
            <div className="flex flex-col gap-1 ml-1">
              {locations[msg.locationIndex].map((loc, locIndex) => (
                <Badge
                  key={locIndex}
                  variant={
                    location?.google_maps_uri === loc.google_maps_uri
                      ? "secondary"
                      : "outline"
                  }
                  className="flex items-center gap-1 cursor-pointer px-2"
                  onClick={() => {
                    if (loc.latitude && loc.longitude) {
                      setLocation(loc);
                      console.log(messageRef);
                      ref.current?.scrollIntoView({
                        behavior: "smooth",
                      });
                    }
                  }}
                >
                  <MapPin size={10} />
                  <span className="text-xs truncate max-w-[100px]">
                    {loc.name}
                  </span>
                </Badge>
              ))}
            </div>
          )}
        </div>
        {location && (
          <div className="mt-2 relative max-w-[450px]">
            <button
              onClick={() => {
                setLocation(null);
                ref.current?.scrollIntoView({ behavior: "smooth" });
              }}
              className="absolute top-2 left-2 z-10 cursor-pointer"
              aria-label="Close map"
            >
              <CircleX />
            </button>
            <a
              href={location.google_maps_uri}
              target="_blank"
              rel="noopener noreferrer"
              className="absolute top-2 right-2 z-10 cursor-pointer"
              aria-label="Open location link"
            >
              <Share />
            </a>
            <div
              className="rounded-full overflow-hidden border border-muted-foreground/20"
              style={{ width: "400px", height: "400px" }}
            >
              <GoogleEarthViewer
                lat={location.latitude!}
                lng={location.longitude!}
                label={location.name}
              />
            </div>
          </div>
        )}
        <div ref={ref}></div>
      </div>
    </div>
  );
}
