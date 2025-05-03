import { Router } from 'express';
import { Message, trips, TripT, AIMessageResponse } from '../db';
import { Server } from 'socket.io';


const tripRouter = Router();

tripRouter.post<{}, {}, {
    username: string, name: string, location: {
        name: string;
        lat: number;
        lng: number;
    }
}>('/', (req, res) => {
    console.log('Creating trip with body:', req.body);
    const { username, name, location } = req.body;

    if (!username || !name || !location) {
        res.status(400).json({ error: 'Missing required fields' });
    }


    const generatedTripCode = Math.random()
        .toString(36)
        .substring(2, 8)
        .toUpperCase();

    const trip: TripT = {
        id: generatedTripCode,
        name,
        creator: username,
        location,
        users: [username],
        started: false,
        locations: [],
        chat: {
            messages: [] as Message[],
        }
    }
    trips.push(trip);
    res.status(201).json(trip);
});

tripRouter.get<{ id: string }>('/:id', (req, res) => {
    const tripId = req.params.id;
    const trip = trips.find(t => t.id === tripId);

    if (!trip) {
        res.status(404).json({ error: 'Trip not found' });
    }

    res.json(trip);
});

tripRouter.post<{ id: string }>('/:id/join', (req, res) => {
    const tripId = req.params.id;
    const { username } = req.body;

    const trip = trips.find(t => t.id === tripId);

    if (!trip) {
        res.status(404).json({ error: 'Trip not found' });
        return;
    }

    if (!username) {
        res.status(400).json({ error: 'Missing required fields' });
        return;
    }

    trip.users.push(username);
    res.status(200).json(trip);
});

export default tripRouter;

export function setupTripWS(io: Server) {
    const tripNamespace = io.of('/trip');
    type SocketData = {
        tripId: string;
        username: string;
    }
    const connectedUsers = new Map<string, SocketData>();



    tripNamespace.on('connection', (socket) => {
        console.log('User connected to trip namespace:', socket.id);

        console.log(trips);

        socket.on('joinTrip', ({ tripId, username }: { tripId: string, username: string }) => {
            socket.join(tripId);
            connectedUsers.set(socket.id, { tripId, username });

            const trip = trips.find(t => t.id === tripId);

            if (!trip) {
                tripNamespace.to(socket.id).emit('error', 'Trip not found');
                return;
            }
            console.log(`User ${username} joined trip ${tripId}`);

            tripNamespace.to(tripId).emit('tripUpdate', trip);
        });

        socket.on('startTrip', ({ tripId }: { tripId: string }) => {
            const trip = trips.find(t => t.id === tripId);
            console.log('Starting trip:', trip);
            if (!trip) {
                tripNamespace.to(socket.id).emit('error', 'Trip not found');
                return;
            }

            trip.started = true;

            tripNamespace.to(tripId).emit('tripStarted', tripId);
        });

        socket.on('huh', () => {
            console.log('Huh event received');
        })

        socket.on('disconnect', () => {
            // const userData = connectedUsers.get(socket.id);
            // if (!userData) return;

            // const { tripId } = userData;
            // const trip = trips.find(t => t.id === tripId);

            // if (trip) {
            //     trip.users = trip.users.filter(user => user !== socket.id);
            //     tripNamespace.to(tripId).emit('tripUpdate', trip);
            // }

            // connectedUsers.delete(socket.id);
            // console.log(`User ${socket.id} disconnected from trip namespace`);
        });

        socket.on('message', async ({ username, tripId, message }: { username: string, tripId: string, message: string }) => {
            const trip = trips.find(t => t.id === tripId);

            if (!trip) {
                tripNamespace.to(socket.id).emit('error', 'Trip not found');
                return;
            }

            const newMessage = {
                sender: username,
                content: message,
                timestamp: new Date()
            };

            trip.chat.messages.push(newMessage);

            tripNamespace.to(tripId).emit('tripUpdate', trip);

            const body = {
                conversation_id: tripId,
                participants: trip.users,
                messages: trip.chat.messages.map(msg => ({
                    role: msg.sender,
                    content: msg.content,
                })),
                location: {
                    latitude: 45.464664,
                    longitude: 9.188540,
                },
                pot: trip.pot,
            }

            console.log('Request body:', body);

            const response = await fetch('http://localhost:8000/chat', {
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

            const data = await response.json() as AIMessageResponse;
        
            console.log(data);

            const aiMessage: Message = {
                sender: 'AI',
                content: data.message,
                timestamp: new Date(),
            }

            if (data.pot) {
                trip.pot = data.pot
            }

            if (data.locations && data.locations.length > 0) {
                aiMessage.locationIndex = trip.locations.length;
                trip.locations.push(data.locations);
            }
            
            
            trip.chat.messages.push(aiMessage);

            tripNamespace.to(tripId).emit('tripUpdate', trip);
        });

        socket.on('usertyping', ({ tripId, username }: { tripId: string, username: string }) => {
            const trip = trips.find(t => t.id === tripId);

            if (!trip) {
                tripNamespace.to(socket.id).emit('error', 'Trip not found');
                return;
            }

            tripNamespace.to(tripId).emit('userTyping', { username });
        });

        socket.on('userstoppedtyping', ({ tripId, username }: { tripId: string, username: string }) => {
            const trip = trips.find(t => t.id === tripId);

            if (!trip) {
                tripNamespace.to(socket.id).emit('error', 'Trip not found');
                return;
            }

            tripNamespace.to(tripId).emit('userStoppedTyping', { username });
        });
    });
}

