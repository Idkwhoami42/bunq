import express from 'express';
import { errorHandler } from './middlewares/errorHandler';
import tripRouter from './routes/trip';
import googleRouter from './routes/google';
const app = express();

export const router = express.Router();

app.use(express.json());

app.use("/trip", tripRouter);
app.use("", googleRouter);

app.use(errorHandler);

export default app;