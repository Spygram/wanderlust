import mongoose from 'mongoose';
import { MONGODB_URI, MONGODB_DB_NAME, MONGODB_USER, MONGODB_PASSWORD } from './utils.js';

export default async function connectDB() {
  try {
    await mongoose.connect(MONGODB_URI as string, {
      dbName: MONGODB_DB_NAME ?? 'wanderlust',
      authSource: 'admin',
      user: MONGODB_USER,
      pass: MONGODB_PASSWORD,
    });
    console.log(`Database connected to: ${MONGODB_DB_NAME ?? 'wanderlust'}`);
  } catch (err: any) {
    console.error(err.message);
    process.exit(1);
  }

  const dbConnection = mongoose.connection;

  dbConnection.on('error', (err) => {
    console.error(`connection error: ${err}`);
  });
  return;
}
