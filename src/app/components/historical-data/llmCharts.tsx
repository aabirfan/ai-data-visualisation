import { useState, useRef, useEffect } from "react";
import Highcharts from "highcharts";
import ChartInput from "./chartInput";
import HighchartsReact from 'highcharts-react-official';

import { Chart, ChartOptions, DateAdapter} from 'chart.js/auto';
import 'chartjs-adapter-moment';
import "../styles/llmCharts.css";
import "../styles/charts.css";

interface ApiResponse {
  message?: any; 
  error?: string;
}

interface HighchartsCodeRendererProps {
  code: string; 
}

interface ChartJsCodeRendererProps {
  code: string;
}

const ChartJs: React.FC<ChartJsCodeRendererProps> = ({ code }) => {
  const [chartData, setChartData] = useState<any | null>(null);
  const chartRef = useRef<HTMLCanvasElement | null>(null);
  const [chartOptions, setChartOptions] = useState<any | null>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (code) {
      try {
        const parsedCode = JSON.parse(code);
        setChartData(parsedCode.data); 
        setChartOptions(parsedCode.options);
      } catch (error) {
        console.error("Error parsing the chart options:", error);
      }
    }
  }, [code]);

  useEffect(() => {
    if (chartData && chartOptions && chartRef.current) {

      if (chartInstance.current) {
        chartInstance.current.destroy(); 
      }

      console.log(chartData)

      const chartType = chartData?.type || 'line';
      console.log('Chart type being used:', chartType);

      chartInstance.current = new Chart(chartRef.current, {
        type: chartType, 
        options: chartOptions,
        data: chartData,
      });
    }
  }, [chartData, chartOptions]);

  if (!chartData) {
    return <p>Loading chart...</p>;
  }

  return (
    <div className="graph-container">
      <canvas ref={chartRef} />
    </div>
  );
};



const HighchartsCodeRenderer: React.FC<HighchartsCodeRendererProps> = ({ code }) => {
  const [options, setOptions] = useState<Highcharts.Options | null>(null);

  useEffect(() => {
    if (code) {
      try {
        const parsedOptions: Highcharts.Options = JSON.parse(code);
        setOptions(parsedOptions);
      } catch (error) {
        console.error("Error parsing the chart options:", error);
      }
    }
  }, [code]);

  if (!options) {
    return <p>Loading chart...</p>;
  }

  return (
    <div className="graph-container">
      <HighchartsReact highcharts={Highcharts} options={options} />
    </div>
  );
};

export default function LLMCharts() {
  const [response, setResponse] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChartRequest = async (query: string | number[]) => {
    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data: ApiResponse = await res.json();

      if (!res.ok) {
        setResponse("Unexpected error occurred.");
      } else {

        if (typeof data.message === "string") {
          data.message = data.message.replace(/```typescript|```|json/g, "");
        }

        setResponse(data.message || "No Data Available.");
        console.log(data.message);
      }
    } catch (error) {
      console.error("Error sending request:", error);
      setResponse("An error occurred while processing your request.");
    }

    setLoading(false);
  };

  return (
    <div className="llm-container">
      <ChartInput onSubmit={handleChartRequest} />
      <div className="llm-content">
        {loading && <p className="loading">Fetching data...</p>}
          {response && <ChartJs code={response} />}
      </div>
    </div>
  );
}
