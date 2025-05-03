// This file can contain any database schema/model definitions if needed
// For example, using an ORM like Sequelize or Prisma
// This is a placeholder
// export interface ChatMessage {
//     message: string;
//     sender: string;
//     room: string;
//     timestamp: Date;
// }

// export interface Message {
//     room: string;
//     content: string;
//     author: string;
// }

// src/types.ts

// Socket.IO event types for type safety
export interface ServerToClientEvents {
    userJoined: (data: {
        user: string;
        users: User[];
        messages: Message[];
    }) => void;
    userLeft: (data: {
        user: string;
        users: User[];
    }) => void;
    newMessage: (message: Message) => void;
    userTyping: (data: {
        username: string;
        isTyping: boolean;
    }) => void;
}

export interface ClientToServerEvents {
    join: (data: {
        username: string;
        room: string;
    }) => void;
    sendMessage: (message: string) => void;
    typing: (isTyping: boolean) => void;
}

// Data models
export interface UserData {
    username: string;
    room: string;
}

export interface User {
    id: string;
    username: string;
}

export interface Message {
    id: string;
    text: string;
    sender: string;
    timestamp: string;
    room: string;
}

export interface RoomData {
    users: User[];
    messages: Message[];
}

export interface RoomInfo {
    name: string;
    userCount: number;
}

export interface ParticipantAmount {
    participant: string;
    currency: string;
    expected_amount: number;
    amount_contributed: number;
}

export interface IndividualGoal {
    description: string;
    participant_amounts: ParticipantAmount[];
}

export interface SharedGoal {
    description: string;
    currency: string;
    expected_amount: number;
    amount_contributed: number;
}

export interface Pot {
    description: string;
    individual_goals: IndividualGoal[];
    shared_goals: SharedGoal[];
}

export interface AIMessageResponse {
    message: string;
    pot: Pot;
}

export interface MessageContent {
    role: string;
    content: string;
}

export interface Location {
    latitude: number;
    longitude: number;
}

export interface AIMessageRequest {
    conversation_id: string;
    participants: string[];
    location: Location;
    messages: MessageContent[];
    pot?: Pot;
}