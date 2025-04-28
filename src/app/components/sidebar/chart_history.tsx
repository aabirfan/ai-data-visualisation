import '../../styles/Sidebar/sidebar-lists.css'; 
import { useState, useEffect } from 'react';
import { LiaHistorySolid } from "react-icons/lia";
import { useChartContext } from '@/app/context/chartContext';
import { SmallDialog } from '@/app/modals/dialog_modal';

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
    setIsNew,
    isClearModalOpen,
    setIsClearModalOpen
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

  const clearChartHistory = async () => {
    if (!selectedAsset) return;
    try {
      const response = await fetch("http://localhost:8000/api/clear-chart-history/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asset_id: selectedAsset }),
      });
      if (!response.ok) {
        throw new Error("Failed to clear chart history");
      }
      setChartHistoryList([]); 
    } catch (error: any) {
      console.error("Error clearing chart history:", error);
      setError(error.message);
    }
  };

  return (
    <div className="lists-container">
      <div className="list-title" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
    <LiaHistorySolid className="list-title-icon" />
    <h1>Chart History</h1>
  </div>
  {selectedAsset && (
    <button onClick={() => setIsClearModalOpen(true)} className="clear-history-button">
    Clear
  </button>  
  )}
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
      
      <SmallDialog isOpen={isClearModalOpen} onClose={() => setIsClearModalOpen(false)}>
  <div className="modal-title">
  <h2><strong>Are you sure you want to clear chart<br /> history?</strong></h2>
  </div>
  <div className="cfm-btn">
    <button onClick={() => setIsClearModalOpen(false)}>No</button>
    <button onClick={async () => {
      await clearChartHistory();
      setIsClearModalOpen(false);
    }}>
      Yes, clear
    </button>
  </div>
</SmallDialog>
    </div>
  );
}
