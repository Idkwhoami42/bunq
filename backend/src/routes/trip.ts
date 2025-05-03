import { Request, Response, Router } from 'express';
import { trips } from '../db';
import { Server } from 'socket.io';


const tripRouter = Router();

tripRouter.post('/', (req: Request, res: Response) => {
    console.log('Creating trip with body:', req.body);
    const { username, name, location } = req.body;

    if (!username || !name || !location) {
        res.status(400).json({ error: 'Missing required fields' });
    }
    const generatedTripCode = Math.random()
        .toString(36)
        .substring(2, 8)
        .toUpperCase();

    const trip = {
        id: generatedTripCode,
        name,
        creator: username,
        location,
        users: [username],
    }
    trips.push(trip);
    res.status(201).json(trip);
});

tripRouter.get('/:id', (req: Request, res: Response) => {
    const tripId = req.params.id;
    const trip = trips.find(t => t.id === tripId);

    if (!trip) {
        res.status(404).json({ error: 'Trip not found' });
    }

    res.json(trip);
});

tripRouter.post('/:id/join', (req: Request, res: Response) => {
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

            if (!trip) {
                tripNamespace.to(socket.id).emit('error', 'Trip not found');
                return;
            }

            tripNamespace.to(tripId).emit('tripStarted', trip);
        });

        socket.on('disconnect', () => {
            const userData = connectedUsers.get(socket.id);
            if (!userData) return;

            const { tripId } = userData;
            const trip = trips.find(t => t.id === tripId);

            if (trip) {
                trip.users = trip.users.filter(user => user !== socket.id);
                tripNamespace.to(tripId).emit('tripUpdate', trip);
            }

            connectedUsers.delete(socket.id);
            console.log(`User ${socket.id} disconnected from trip namespace`);
        });
    });
}

