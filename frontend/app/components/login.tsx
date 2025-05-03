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
import { toast } from "sonner";
import { useNavigate } from "react-router";

export default function LoginPage() {
  const [chatID, setChatID] = useState("");
  const [userToken, setUserToken] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Validate inputs
    if (!chatID.trim()) {
      toast("Missing Chat ID", {
        description: "Please enter a Chat ID",
        // variant: "destructive",
      });
      return;
    }

    if (!userToken.trim()) {
      toast("Missing User Token", {
        description: "Please enter a User Token",
        // variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    // Simulate authentication process
    setTimeout(() => {
      // Store values in sessionStorage
      sessionStorage.setItem("chatID", chatID);
      sessionStorage.setItem("userID", userToken);

      navigate("/chat");

      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-xl text-center">Chat Login</CardTitle>
          <CardDescription className="text-center">
            Enter your Chat ID and User Token to continue
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="chatID">Chat ID</Label>
              <Input
                id="chatID"
                placeholder="Enter your Chat ID"
                value={chatID}
                onChange={(e) => setChatID(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="userToken">User Token</Label>
              <Input
                id="userToken"
                type="password"
                placeholder="Enter your User Token"
                value={userToken}
                onChange={(e) => setUserToken(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </CardContent>
          <CardFooter className="mt-5">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Connecting..." : "Connect to Chat"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
