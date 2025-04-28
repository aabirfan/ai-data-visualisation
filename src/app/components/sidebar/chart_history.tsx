import '../../styles/Sidebar/sidebar-lists.css'; 
import { useState, useEffect } from 'react';
import { LiaHistorySolid } from "react-icons/lia";
import { useChartContext } from '@/app/context/chartContext';

export async function fetchHistoryData(asset_id: string): Promise<any[]> {
  try {
    const response = await fetch("http://localhost:8000/get_chart_history", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ asset_id }),
    });
    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }
    const data = await response.json();
    return data.data; 
  } catch (error: any) {
    console.error("Fetch error:", error);
    throw new Error(error.message); 
  }
}

export default function ChartHistory() {
  const {
    selectedAsset,
    loading,
    setLoading,
    error,
    setError,
    setChartHistoryList,
    chartHistoryList,
    setChartData,
    setChartOptions,
    setChartType,
    setChartTitle,
    activeChart,
    setActiveChart,
    setPreviousQuery,
    setIsSaved,
    setIsNew
  } = useChartContext();


  const handleChartClick = (chart:any) => {
    setChartData(chart.chartData);
    setChartOptions(chart.chartOptions);
    setChartType(chart.chartType);
    setChartTitle(chart.title);
    setActiveChart(chart);
    setPreviousQuery(chart.previousQueries);
    setIsSaved(false);
    setIsNew(false);
  }


  useEffect(() => {
    const loadHistoryData = async () => {
      if (selectedAsset) {
        try {
          const historyData = await fetchHistoryData(selectedAsset);
          setChartHistoryList(historyData);
        } catch (error: any) {
          setError(error.message);
        } finally {
        }
      }
    };
    loadHistoryData();
  }, [selectedAsset]);

  return (
    <div className="lists-container">
      <div className="list-title">
        <LiaHistorySolid className="list-title-icon" />
        <h1>Chart History</h1>
      </div>
  
      {error ? (
        <p>Error: {error}</p>
      ) : (
        <div className="list-content">
          {chartHistoryList.length === 0 ? (
            <p>No chart history</p>
          ) : (
            <ul>
            {[...chartHistoryList].reverse().map((chart, index) => (
              <li key={index}>
                <button
                  className={`archived-chart-button ${activeChart === chart ? 'active' : ''}`} 
                  onClick={() => handleChartClick(chart)}
                >
                  <h2>{chart.title}</h2>
                </button>
              </li>
            ))}
          </ul>
          )}
        </div>
      )}
    </div>
  );
}
