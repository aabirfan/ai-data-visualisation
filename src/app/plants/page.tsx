"use client";

import { useEffect, useState } from "react";

export default function PlantsPage() {
    const [plant1, setPlant1] = useState<any[]>([]);
    const [plant2, setPlant2] = useState<any[]>([]);
    const [page, setPage] = useState(1);
    const limit = 50; // Adjust as needed

    useEffect(() => {
        fetch(`/api/plants?page=${page}&limit=${limit}`)
            .then((res) => res.json())
            .then((data) => {
                setPlant1(data.Plant1 || []);
                setPlant2(data.Plant2 || []);
            })
            .catch((error) => console.error("Error fetching plant data:", error));
    }, [page]);

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold">Plant Sensor Data</h1>

            {/* Table for Plant 1 */}
            <h2 className="text-xl font-semibold mt-4">🌱 Plant 1 Data</h2>
            <table className="border-collapse border border-gray-300 w-full">
                <thead>
                    <tr className="bg-gray-100">
                        <th className="border p-2">Type</th>
                        <th className="border p-2">Timestamp</th>
                        <th className="border p-2">Value</th>
                    </tr>
                </thead>
                <tbody>
                    {plant1.map((plant, index) => (
                        <tr key={index} className="border">
                            <td className="border p-2">{plant.type}</td>
                            <td className="border p-2">{new Date(plant.timestamp).toLocaleString()}</td>
                            <td className="border p-2">{plant.value}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Table for Plant 2 */}
            <h2 className="text-xl font-semibold mt-4">🌿 Plant 2 Data</h2>
            <table className="border-collapse border border-gray-300 w-full">
                <thead>
                    <tr className="bg-gray-100">
                        <th className="border p-2">Type</th>
                        <th className="border p-2">Timestamp</th>
                        <th className="border p-2">Value</th>
                    </tr>
                </thead>
                <tbody>
                    {plant2.map((plant, index) => (
                        <tr key={index} className="border">
                            <td className="border p-2">{plant.type}</td>
                            <td className="border p-2">{new Date(plant.timestamp).toLocaleString()}</td>
                            <td className="border p-2">{plant.value}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Pagination Buttons */}
            <div className="flex justify-between mt-4">
                <button disabled={page === 1} onClick={() => setPage(page - 1)} className="p-2 bg-gray-300 rounded">⬅️ Previous</button>
                <button onClick={() => setPage(page + 1)} className="p-2 bg-gray-300 rounded">Next ➡️</button>
            </div>
        </div>
    );
}
