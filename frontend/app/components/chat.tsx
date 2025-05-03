import type React from "react";

import { useState, useRef, useEffect, use, useCallback } from "react";
import { Send, Share, UserPlus } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { toast } from "sonner";
import cuid2 from "@paralleldrive/cuid2";
import { io, Socket } from "socket.io-client";
import { useNavigate } from "react-router";

interface Message {
  id: string;
  text: string;
  sender: string;
  timestamp: string;
  room: string;
}

interface User {
  id: string;
  username: string;
}

interface TypingUser {
  username: string;
  isTyping: boolean;
}

interface ChatRoomProps {
  chatID: string; // The room ID
  userID: string; // The user's ID (used as username)
}

// Socket event types
interface ServerToClientEvents {
  userJoined: (data: {
    user: string;
    users: User[];
    messages: Message[];
  }) => void;
  userLeft: (data: { user: string; users: User[] }) => void;
  newMessage: (message: Message) => void;
  userTyping: (data: { username: string; isTyping: boolean }) => void;
}

interface ClientToServerEvents {
  join: (data: { username: string; room: string }) => void;
  sendMessage: (message: string) => void;
  typing: (isTyping: boolean) => void;
}

export default function ChatUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);
  const [message, setMessage] = useState<string>("");
  const [socket, setSocket] = useState<Socket<
    ServerToClientEvents,
    ClientToServerEvents
  > | null>(null);
  const [connected, setConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [userID, setUserID] = useState<string | null>(null);
  const [chatID, setChatID] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    const storedUserID = sessionStorage.getItem("userID");
    const storedChatID = sessionStorage.getItem("chatID");

    if (!storedUserID || !storedChatID) {
      toast.error("User ID or Chat ID not found in session storage.");
      navigate("/");
      return;
    }

    setUserID(storedUserID);
    setChatID(storedChatID);

    const socketInstance = io("http://localhost:3000", {
      transports: ["websocket"],
      autoConnect: true,
    });

    socketInstance.on("connect", () => {
      console.log("Connected to chat server");
      setConnected(true);
      setError(null);

      // Join the chat room
      socketInstance.emit("join", {
        username: storedUserID,
        room: storedChatID,
      });
    });

    socketInstance.on("connect_error", (err) => {
      console.error("Connection error:", err);
      setConnected(false);
      setError(`Failed to connect: ${err.message}`);
    });

    socketInstance.on("disconnect", () => {
      console.log("Disconnected from chat server");
      setConnected(false);
    });

    // Store socket instance in state
    setSocket(
      socketInstance as Socket<ServerToClientEvents, ClientToServerEvents>
    );

    // Cleanup on unmount
    return () => {
      socketInstance.disconnect();
    };
  }, []);

  // Set up event listeners for chat events once socket is available
  useEffect(() => {
    if (!socket) return;

    console.log("Socket initialized");

    // Handle user joined event
    socket.on("userJoined", ({ user, users, messages: roomMessages }) => {
      console.log(`${user} joined the room`);
      setUsers(users);
      setMessages(roomMessages);
    });

    // Handle user left event
    socket.on("userLeft", ({ user, users }) => {
      console.log(`${user} left the room`);
      setUsers(users);
      setTypingUsers((current) => current.filter((u) => u.username !== user));
    });

    // Handle new message event
    socket.on("newMessage", (message) => {
      console.log(`New message from ${message.sender}: ${message.text}`);
      setMessages((current) => [...current, message]);

      // If the message sender was typing, remove them from typing users
      if (message.sender !== userID) {
        setTypingUsers((current) =>
          current.map((u) =>
            u.username === message.sender ? { ...u, isTyping: false } : u
          )
        );
      }
    });

    // Handle typing indicator
    socket.on("userTyping", ({ username, isTyping }) => {
      console.log(`${username} is ${isTyping ? "typing" : "stopped typing"}`);
      setTypingUsers((current) => {
        const userExists = current.some((u) => u.username === username);

        if (userExists) {
          return current.map((u) =>
            u.username === username ? { ...u, isTyping } : u
          );
        } else if (isTyping) {
          return [...current, { username, isTyping }];
        }

        return current;
      });
    });

    return () => {
      // Remove all listeners on cleanup
      socket.off("userJoined");
      socket.off("userLeft");
      socket.off("newMessage");
      socket.off("userTyping");
    };
  }, [socket, userID]);

  // Send message handler
  const sendMessage = useCallback((e) => {
    e.preventDefault();
    if (!socket || !message.trim()) return;

    socket.emit("sendMessage", message);
    setMessage("");
  }, [socket, message]);

  // Typing indicator handler
  const handleTyping = useCallback(
    (isTyping: boolean) => {
      if (!socket) return;
      socket.emit("typing", isTyping);
    },
    [socket]
  );

  // Handle message input change
  const handleMessageChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setMessage(e.target.value);

      // Send typing indicator
      if (e.target.value.length > 0) {
        handleTyping(true);
      } else {
        handleTyping(false);
      }
    },
    [handleTyping]
  );

  return (
    <>
      <div>
        User ID: {userID}
        <br />
        Chat ID: {chatID}
        <br />
        Users: {JSON.stringify(users)}
        <form onSubmit={sendMessage} className="flex items-center gap-2">
          <Input
            value={message}
            onChange={handleMessageChange}
            placeholder="Type a message..."
            className="flex-1"
          />
          <Button type="submit" size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </form>
        <br />
        Messages:
        {messages.map((msg) => (
          <div key={msg.id} className="flex">
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.sender === userID
                  ? "bg-primary text-primary-foreground"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              <p className="text-sm">{msg.text}</p>
            </div>
          </div>
        ))}
        {typingUsers.map((user) => (
          <div key={user.username} className="text-sm text-gray-500">
            {user.isTyping ? `${user.username} is typing...` : null}
          </div>
        ))}
        {error && <div className="text-red-500">{error}</div>}
        {connected ? (
          <div className="text-green-500">Connected</div>
        ) : (
          <div className="text-red-500">Disconnected</div>
        )}
      </div>
    </>
  );

  // return (
  //   <div className="flex flex-col h-full bg-gray-50">
  //     {/* Header */}
  //     <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3 shadow-sm flex items-center justify-between">
  //       <h1 className="text-lg font-medium">Chat</h1>
  //       <Button variant="outline" size="sm">
  //         <UserPlus className="h-4 w-4 mr-2" />
  //         Invite
  //       </Button>
  //     </header>

  //     {/* User List */}
  //     <div className="bg-white border-b border-gray-200 px-4 py-2 overflow-x-auto">
  //       <div className="flex items-center space-x-4">
  //         {users.map((user) => (
  //           <div
  //             key={user.id}
  //             className="text-sm text-gray-700 rounded-full bg-gray-100 px-3 py-1"
  //           >
  //             {user.name}
  //           </div>
  //         ))}
  //       </div>
  //     </div>

  //     {/* Messages */}
  //     <div className="flex-1 overflow-y-auto p-4 space-y-4">
  //       {messages.length === 0 ? (
  //         <div className="flex items-center justify-center h-full text-gray-500">
  //           <p>Send a message to start chatting</p>
  //         </div>
  //       ) : (
  //         messages.map((message) => (
  //           <div
  //             key={message.id}
  //             className={`flex ${
  //               message.role === "user" ? "justify-end" : "justify-start"
  //             }`}
  //           >
  //             <div
  //               className={`max-w-[80%] rounded-lg px-4 py-2 ${
  //                 message.role === "user"
  //                   ? "bg-primary text-primary-foreground"
  //                   : "bg-gray-200 text-gray-800"
  //               }`}
  //             >
  //               <p className="text-sm">{message.content}</p>
  //             </div>
  //           </div>
  //         ))
  //       )}
  //       {isLoading && (
  //         <div className="flex justify-start">
  //           <div className="max-w-[80%] rounded-lg px-4 py-2 bg-gray-200 text-gray-800">
  //             <div className="flex space-x-1">
  //               <div
  //                 className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
  //                 style={{ animationDelay: "0ms" }}
  //               ></div>
  //               <div
  //                 className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
  //                 style={{ animationDelay: "150ms" }}
  //               ></div>
  //               <div
  //                 className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
  //                 style={{ animationDelay: "300ms" }}
  //               ></div>
  //             </div>
  //           </div>
  //         </div>
  //       )}
  //       <div ref={messagesEndRef} />
  //     </div>

  //     {/* Input area */}
  //     <div className="sticky bottom-0 bg-white border-t border-gray-200 p-3">
  //       <form onSubmit={handleSubmit} className="flex items-center gap-2">
  //         <Input
  //           value={input}
  //           onChange={handleInputChange}
  //           placeholder="Type a message..."
  //           className="flex-1"
  //           disabled={isLoading}
  //         />
  //         <Button type="submit" size="icon" disabled={isLoading}>
  //           <Send className="h-4 w-4" />
  //         </Button>
  //       </form>
  //     </div>
  //   </div>
  // );
}
