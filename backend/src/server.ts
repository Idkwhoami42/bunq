import app from './app';
import config from './config/config';
import http from 'http';
import { Server } from 'socket.io';
import { setupTripWS } from './routes/trip';

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  }
});

setupTripWS(io);

server.listen(config.port, () => {
  console.log(`Server is running on port ${config.port}`);
});

export { io };