
import { Server, Socket } from 'socket.io';
import {
    UserData,
    User,
    Message,
    RoomData,
    ServerToClientEvents,
    ClientToServerEvents,
    AIMessageRequest,
    AIMessageResponse
} from '../types/chat';

export function initializeSocketIO(io: Server) {
    // Store active users and rooms
    const connectedUsers = new Map<string, UserData>();
    const rooms = new Map<string, RoomData>();

    // Socket.IO connection handling
    io.on('connection', (socket: Socket<ClientToServerEvents, ServerToClientEvents>) => {
        console.log(`User connected: ${socket.id}`);

        // User joins with username
        socket.on('join', ({ username, room }: { username: string, room: string }) => {
            // Store user data
            connectedUsers.set(socket.id, { username, room });

            // Join room
            socket.join(room);

            // Initialize room if doesn't exist
            if (!rooms.has(room)) {
                rooms.set(room, { users: [], messages: [] });
            }

            // Add user to room
            const roomData = rooms.get(room)!;
            roomData.users.push({ id: socket.id, username });

            // Notify everyone in the room
            io.to(room).emit('userJoined', {
                user: username,
                users: roomData.users,
                messages: roomData.messages
            });

            console.log(`${username} joined room: ${room}`);
        });

        // Handle incoming messages
        socket.on('sendMessage', async (message: string) => {
            const userData = connectedUsers.get(socket.id);

            if (!userData) return;

            const { username, room } = userData;
            const roomData = rooms.get(room);

            if (!roomData) return;

            const timestamp = new Date().toISOString();

            const newMessage: Message = {
                id: `msg-${Date.now()}-${socket.id.substring(0, 4)}`,
                text: message,
                sender: username,
                timestamp,
                room
            };

            roomData.messages.push(newMessage);

            io.to(room).emit('newMessage', newMessage);

            // // Broadcast message to room
            // io.to(room).emit('newMessage', newMessage);

            const body: AIMessageRequest = {
                conversation_id: room,
                participants: roomData.users.map(user => user.username),
                messages: roomData.messages.map(msg => ({
                    role: msg.sender,
                    content: msg.text,
                })),
                location: {
                    latitude: 45.464664,
                    longitude: 9.188540,
                }
            }

            console.log('Request body:', body);

            const response = await fetch('http://192.168.65.37:8080/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            })

            if (!response.ok) {
                console.error('Error:', response.statusText);
                return;
            }

            const data = await response.json() satisfies AIMessageResponse;

            const aiMessage: Message = {
                id: `msg-${Date.now()}-${socket.id.substring(0, 4)}`,
                text: data.message,
                sender: 'AI',
                timestamp,
                room
            }
            roomData.messages.push(aiMessage);

            io.to(room).emit('newMessage', aiMessage);

            console.log(`Message from ${username} in ${room}: ${message}`);
        });

        // Handle typing indicators
        socket.on('typing', (isTyping: boolean) => {
            const userData = connectedUsers.get(socket.id);
            if (!userData) return;

            const { username, room } = userData;
            socket.to(room).emit('userTyping', { username, isTyping });
        });

        // Handle user disconnection
        socket.on('disconnect', () => {
            const userData = connectedUsers.get(socket.id);
            if (!userData) return;

            const { username, room } = userData;

            // Remove user from room
            const roomData = rooms.get(room);
            if (roomData) {
                roomData.users = roomData.users.filter(user => user.id !== socket.id);

                // If room is empty, clean it up
                if (roomData.users.length === 0) {
                    rooms.delete(room);
                } else {
                    // Notify others in room
                    io.to(room).emit('userLeft', {
                        user: username,
                        users: roomData.users
                    });
                }
            }

            // Remove from connected users
            connectedUsers.delete(socket.id);

            console.log(`User disconnected: ${username}`);
        });
    });

}