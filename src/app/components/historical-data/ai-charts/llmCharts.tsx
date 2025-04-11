import { useState, useRef, useEffect } from "react";
import {sanitizeInput, ChartInput} from "./chartInput";
import { saveGraph } from "../../../utils/archive_graph";
import { Chart } from 'chart.js/auto';
import { handleChartRequest } from "../../../utils/chartUtils";
import {Dialog} from "@/app/modals/dialog_modal";
import PromptSuggestions from "./promptSuggestions";

import 'chartjs-adapter-moment';
import "../../../styles/llmCharts.css";
import "../../../styles/charts.css";
import "../../../styles/modals.css";

interface ChartJsCodeRendererProps {
  chartData: any;
  chartOptions: any;
  chartType: any;
  textResponse?: string | null; 
  userQuery: string;
}

interface llmChartProps {
  loading: boolean; 
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  selectedAsset: string; 
}


const ChartJs: React.FC<ChartJsCodeRendererProps> = ({
  chartData,
  chartOptions,
  chartType,
  textResponse,
  userQuery,
}) => {
  const chartRef = useRef<HTMLCanvasElement | null>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (chartData && chartOptions && chartType && chartRef.current) {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }

      chartInstance.current = new Chart(chartRef.current, {
        type: chartType,
        data: chartData,
        options: chartOptions,
      });
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [chartData, chartOptions, chartType]);

  if (textResponse) {
    return (
      <div className="chat-container">
        <div className="query-box">
          <p>{userQuery}</p>
        </div>
          <div className="text-response">
          <img className="response-img" src="illi_blink.png" alt="bot" />
          <p>{textResponse}</p>
        </div>
      </div>
    );
  }

  if (!chartData || !chartOptions || !chartType) {
    return (
      <div>
        <img className="response-img" src="illi_blink.png" alt="bot" />
        <p>Loading chart</p>
      </div>
    );
  }

  return (
    <div className="graph-container">
      <canvas ref={chartRef} />
    </div>
  );
};

export default ChartJs;

function LLMCharts({ loading, setLoading, selectedAsset}: llmChartProps) {
  const [response, setResponse] = useState<any | null>(null);
  const [chartData, setChartData] = useState<any | null>(null);
  const [chartOptions, setChartOptions] = useState<any | null>(null);
  const [chartType, setChartType] = useState<string>("");
  const [isModalOpen, setModalOpen] = useState(false)
  const [chartTitle, setChartTitle] = useState<string>("");
  const [chartDescription, setChartDescription] = useState<string>("");
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [userQuery, setUserQuery] = useState<string>(""); 

  const handleTitleSave = (savedChartTitle: string) => {
    setChartTitle(sanitizeInput(savedChartTitle));
  }
  
  const handleDescSave = (savedChartDesc: string) => {
    setChartDescription(sanitizeInput(savedChartDesc));
  }



  const openModal = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);

  const savePromptHistory = (query: string ) => {
    if (typeof query !== "string") {
      return; 
    }
    let history = JSON.parse(localStorage.getItem("promptHistory") || "[]");
    history.unshift(query); 
    localStorage.setItem("promptHistory", JSON.stringify(history));
  };
  
  
  return (
    <div className="llm-container">

    <ChartInput 
    onSubmit={(query) => { 
    setUserQuery(query);
    setShowSuggestions(false);
    savePromptHistory(query);
    handleChartRequest(query, selectedAsset, setLoading, setResponse, setChartData, setChartOptions, setChartType, setChartTitle);
  }}
  selectedAsset={selectedAsset}
  loading={loading}
/>
{showSuggestions && (
<PromptSuggestions
  selectedAsset={selectedAsset}
  onSubmit={(query) => {
    setShowSuggestions(false); 
    savePromptHistory(query);
    handleChartRequest(query, selectedAsset, setLoading, setResponse, setChartData, setChartOptions, setChartType, setChartTitle);
  }}
/>
)}
      <Dialog isOpen={isModalOpen} onClose={closeModal}>
            <div className="modal-title">
              <h2>Save Chart...</h2>
            </div>
            <form className="save-chart-input">
              <h3>Title:</h3>
              <input
                type="text"
                placeholder="Enter title..."
                className="save-input"
                value={chartTitle}
                onChange={(e) => handleTitleSave(e.target.value)}
                maxLength={60}
              />
              <h3>Description:</h3>
              <input
                type="text"
                placeholder="Enter description..."
                className="save-input"
                value={chartDescription}
                onChange={(e) => handleDescSave(e.target.value)}
                maxLength={60}
              />
            </form>

            <div className="save-btn">
              <button
                onClick={() => {
                  saveGraph(chartData, chartOptions, chartType, chartTitle, chartDescription, selectedAsset); 
                  setModalOpen(false);
                }}
              >
                Save Chart
              </button>
            </div>
          </Dialog> 

      <div className="llm-content">
        {loading && <p className="loading">
          Fetching data...</p>}
        {response ? (
          response.error ? (
            <div className="error-message">
              <p>{response.error}</p>
              {response.error.includes("Invalid date format") ? (
                <ul>
                  <li>Ensure the date format is <strong>YYYY-MM-DD, DD/MM/YYYY or Day Month Year</strong></li>
                  <li>Example: <strong>2022-09-27, 27/09/2022 or 27 September 2022</strong></li>
                </ul>
              ) : (
                <ul>
                  <li>Try asking for <strong>pH in</strong></li>
                  <li>Try asking for <strong>pH out</strong></li>
                  <li>Try asking for <strong>CO2 usage</strong></li>
                </ul>
              )}
            </div>
          ) : (
            <>
              <ChartJs chartData={chartData} chartOptions={chartOptions} chartType={chartType} textResponse={response?.type === "text" ? response.content : null} 
              userQuery={userQuery} 
              
 />

              <div className="save-btn">
                <button onClick={() => setModalOpen(true)}>Save chart...</button>
              </div>
            </>
          )
        ) : null}
      </div>
    </div>
  );
}

export {LLMCharts, ChartJs}