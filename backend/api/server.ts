import app from '../app.js';
import connectDB from '../config/db.js';
import { connectToRedis } from '../services/redis.js';
import type { IncomingMessage, ServerResponse } from 'http';

export default async function handler(req: IncomingMessage, res: ServerResponse) {
  await connectToRedis();
  await connectDB();

  app(req, res); // Express handles it as a request
}
