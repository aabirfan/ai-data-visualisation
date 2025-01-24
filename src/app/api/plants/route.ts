import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
require('dotenv').config({ path: '.env.local' });
const { GoogleGenerativeAI } = require("@google/generative-ai");


// GEMINI API QUICKSTART 

/* 
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
const prompt = "how many tokens per request";

const result = await model.generateContent(prompt);
console.log(result.response.text());
*/ 


const DEFAULT_PAGE = 1;
const DEFAULT_LIMIT = 25;

interface QueryParams {
    page?: string;
    limit?: string;
}

const formatData = (data: any[]) =>
    data.map(item => ({
        ...item,
        timestamp: item.timestamp instanceof Date ? item.timestamp.toISOString() : item.timestamp
    }));

export async function GET(req: Request) {
    try {
        const { searchParams } = new URL(req.url);
        const queryParams: QueryParams = Object.fromEntries(searchParams);

        const page = Math.max(parseInt(queryParams.page || `${DEFAULT_PAGE}`, 10), 1);
        const limit = Math.max(parseInt(queryParams.limit || `${DEFAULT_LIMIT}`, 10), 1);
        const skip = (page - 1) * limit;

        const db = await connectToDatabase();

        const plant1Data = await db.collection("Plant1").find({})
            .sort({ _id: -1 })
            .skip(skip)
            .limit(limit)
            .toArray();

        const plant2Data = await db.collection("Plant2").find({})
            .sort({ _id: -1 })
            .skip(skip)
            .limit(limit)
            .toArray();

        return NextResponse.json({
            Plant1: formatData(plant1Data),
            Plant2: formatData(plant2Data),
            pagination: { page, limit }
        });

    } catch (error) {
        console.error("Error fetching plant data:", error);
        return NextResponse.json(
            { error: "Failed to fetch plant data" }, 
            { status: 500 }
        );
    }
}
