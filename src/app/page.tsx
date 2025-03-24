"use client";
import Image from "next/image";
import React, { useEffect, useState } from "react";
import ChartTabs from "./components/historical-data/chartTabs";
import AssetPicker from "./components/assetPicker";

export default function Home() {
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [assets, setAssets] = useState<{ id: string; name: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchAssets = async () => {
    try {
      const response = await fetch("http://localhost:8000/assets");
      if (!response.ok) {
        throw new Error("Failed to fetch assets");
      }
      const responseData = await response.json();
      console.log("Fetched data:", responseData); 
      setAssets(responseData.data); 
    } catch (error: any) {
      console.error("Fetch error:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []);

  useEffect(() => {
    if (selectedAsset) {
      console.log("Selected asset changed:", selectedAsset);
    }
  }, [selectedAsset]);

  return (
    <>
      <header>
        <Image
          className="logo"
          alt="Twilligent logo"
          src="/logo.png"
          width={300}
          height={300}
          loading="lazy"
        />
        <AssetPicker
          setSelectedAsset={setSelectedAsset}
          selectedAsset={selectedAsset}
          assets={assets || []}
          />
      </header>
      <main>
        {loading ? (
          <h1>Loading assets...</h1>
        ) : error ? (
          <h1>Error: {error}</h1>
        ) : selectedAsset ? (
          <ChartTabs key={selectedAsset} selectedAsset={selectedAsset}/>
        ) : (
          <h1>Please select an asset</h1>
        )}
      </main>
    </>
  );
}
