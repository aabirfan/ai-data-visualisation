import { MongoClient } from "mongodb";

if (!process.env.MONGODB_URI) {
    throw new Error("MongoDB connection string is missing from .env.local");
}

const client = new MongoClient(process.env.MONGODB_URI);
let db: any;

export async function connectToDatabase() {
    if (!db) {
        await client.connect();
        db = client.db("PlantDatabase"); 
    }
    return db;
}
