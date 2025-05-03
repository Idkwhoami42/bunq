import { useState } from "react";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Label } from "~/components/ui/label";
import { MapPin, Users, PlusCircle, LogIn, ChevronLeft } from "lucide-react";
import { RadioGroup, RadioGroupItem } from "~/components/ui/radio-group";
import { toast } from "sonner";
import { useNavigate } from "react-router";

type Step = "username" | "selection" | "create" | "join";

// Location options with icons
const locations = [
  { id: "beach", name: "Beach", icon: "🏖️" },
  { id: "mountain", name: "Mountain", icon: "🏔️" },
  { id: "city", name: "City", icon: "🏙️" },
  { id: "countryside", name: "Countryside", icon: "🌄" },
  { id: "island", name: "Island", icon: "🏝️" },
];

export default function TripPage() {
  const [step, setStep] = useState<Step>("username");
  const [username, setUsername] = useState("");
  const [tripName, setTripName] = useState("");
  const [location, setLocation] = useState("");
  const [tripCode, setTripCode] = useState("");
  const navigate = useNavigate();

  const handleUsernameSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) {
      toast.error("Username required", {
        description: "Please enter your username to continue",
      });
      return;
    }
    setStep("selection");
  };

  const handleCreateTrip = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tripName.trim()) {
      toast.error("Trip name required", {
        description: "Please enter a name for your trip",
      });
      return;
    }
    if (!location) {
      toast.error("Location required", {
        description: "Please select a location for your trip",
      });
      return;
    }
    await fetch("http://localhost:3000/trip", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        name: tripName,
        location,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Network response was not ok, " + response.statusText
          );
        }
        return response.json();
      })
      .then((data) => {
        sessionStorage.setItem("username", username);
        navigate("/trip/" + data.id);
      })
      .catch((error) => {
        console.error("Error creating trip:", error);
        toast.error("Error creating trip", {
          description: "Please try again later",
        });
      });
  };

  const handleJoinTrip = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tripCode.trim()) {
      toast.error("Trip code required", {
        description: "Please enter a trip code to join",
      });
      return;
    }

    await fetch("http://localhost:3000/trip/" + tripCode + "/join", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Network response was not ok, " + response.statusText
          );
        }
        return response.json();
      })
      .then((data) => {
        sessionStorage.setItem("username", username);
        navigate("/trip/" + data.id);
      })
      .catch((error) => {
        console.error("Error joining trip:", error);
        toast.error("Error joining trip", {
          description: "Please check the trip code and try again",
        });
      });
  };

  const goBack = () => {
    if (step === "selection") {
      setStep("username");
    } else if (step === "create" || step === "join") {
      setStep("selection");
    }
  };

  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md relative">
        {/* Header changes based on current step */}
        <CardHeader>
          {step !== "username" && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute left-4 top-4"
              onClick={goBack}
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
          )}
          <CardTitle className="text-xl text-center">
            {step === "username" && "Welcome to Trip Planner"}
            {step === "selection" && "What would you like to do?"}
            {step === "create" && "Create a New Trip"}
            {step === "join" && "Join an Existing Trip"}
          </CardTitle>
          <CardDescription className="text-center">
            {step === "username" && "Please enter your username to get started"}
            {step === "selection" &&
              "Create a new trip or join an existing one"}
            {step === "create" && "Set up your trip details"}
            {step === "join" && "Enter the trip code to join"}
          </CardDescription>
        </CardHeader>

        <CardContent>
          {/* Username Step */}
          {step === "username" && (
            <form onSubmit={handleUsernameSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <Button type="submit" className="w-full">
                Continue
              </Button>
            </form>
          )}

          {/* Selection Step */}
          {step === "selection" && (
            <div className="space-y-4">
              <Button
                onClick={() => setStep("create")}
                className="w-full flex items-center justify-center gap-2 h-16"
                variant="outline"
              >
                <PlusCircle className="h-5 w-5" />
                <div className="text-left">
                  <div className="font-medium">Create a Trip</div>
                  <div className="text-xs text-muted-foreground">
                    Start planning a new adventure
                  </div>
                </div>
              </Button>

              <Button
                onClick={() => setStep("join")}
                className="w-full flex items-center justify-center gap-2 h-16"
                variant="outline"
              >
                <LogIn className="h-5 w-5" />
                <div className="text-left">
                  <div className="font-medium">Join a Trip</div>
                  <div className="text-xs text-muted-foreground">
                    Join an existing trip with a code
                  </div>
                </div>
              </Button>
            </div>
          )}

          {/* Create Trip Step */}
          {step === "create" && (
            <form onSubmit={handleCreateTrip} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="tripName">Trip Name</Label>
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <Input
                    id="tripName"
                    placeholder="Enter trip name"
                    value={tripName}
                    onChange={(e) => setTripName(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-3">
                <Label>Select Location Type</Label>
                <RadioGroup
                  value={location}
                  onValueChange={setLocation}
                  className="grid grid-cols-3 gap-2"
                >
                  {locations.map((loc) => (
                    <div key={loc.id} className="flex flex-col items-center">
                      <RadioGroupItem
                        value={loc.id}
                        id={loc.id}
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor={loc.id}
                        className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer w-full"
                      >
                        <span className="text-2xl mb-1">{loc.icon}</span>
                        <span className="text-xs font-normal">{loc.name}</span>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>

              <Button type="submit" className="w-full">
                Create Trip
              </Button>
            </form>
          )}

          {/* Join Trip Step */}
          {step === "join" && (
            <form onSubmit={handleJoinTrip} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="tripCode">Trip Code</Label>
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <Input
                    id="tripCode"
                    placeholder="Enter trip code (e.g., ABC123)"
                    value={tripCode}
                    onChange={(e) => setTripCode(e.target.value.toUpperCase())}
                  />
                </div>
              </div>
              <Button type="submit" className="w-full">
                Join Trip
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
