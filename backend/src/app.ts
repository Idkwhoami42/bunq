import express from 'express';
import { errorHandler } from './middlewares/errorHandler';
import tripRouter from './routes/trip';
const app = express();

export const router = express.Router();

app.use(express.json());

app.use("/trip", tripRouter);

app.use(errorHandler);

export default app;