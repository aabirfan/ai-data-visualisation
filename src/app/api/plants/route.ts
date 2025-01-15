import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";

export async function GET() {
    try {
        const db = await connectToDatabase();
        const plant1Data = await db.collection("Plant1").find({}).sort({ _id: -1 }).limit(25).toArray();
        const plant2Data = await db.collection("Plant2").find({}).sort({ _id: -1 }).limit(25).toArray();

        return NextResponse.json({ Plant1: plant1Data, Plant2: plant2Data });
    } catch (error) {
        console.error("Error fetching data:", error);
        return NextResponse.json({ error: "Failed to fetch plant data" }, { status: 500 });
    }
}

