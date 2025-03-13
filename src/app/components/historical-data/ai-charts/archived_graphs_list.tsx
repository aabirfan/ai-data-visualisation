import React, { useState, useEffect, useRef} from 'react';
import "../../../styles/modals.css";
import { ChartJs } from './llmCharts';
import Modal from '@/app/modals/modal';
import { removeGraph } from '@/app/utils/archive_graph';
import { SmallDialog } from '@/app/modals/dialog_modal';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const Archived_Graphs_List: React.FC<ModalProps> = ({ isOpen, onClose }) => {
  const [listData, setListData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  //Preview States
  const [chartData, setChartData] = useState<any | null>(null);
  const [chartOptions, setChartOptions] = useState<any | null>(null);
  const [chartType, setChartType] = useState<string>("line");
  const [chartTitle, setChartTitle] = useState<string>("");
  const [chartDate, setChartDate] = useState<string>("");
  const chartRef = useRef<HTMLCanvasElement | null>(null);


  const [isLModalOpen, setLModalOpen] = useState(false);
  const [isSmodalOpen, setSmodalOpen] = useState(false);

  const openModal = (data: any, type:any, options:any, title:string, date:string) => {
    setLModalOpen(true);
    setChartData(data);
    setChartOptions(options);
    setChartType(type);
    setChartTitle(title)
    setChartDate(date)
  };

  const openSmodal = (date:string) => {
    setSmodalOpen(true)
    setChartDate(date)
  }

  const closeModal = () => setLModalOpen(false);

  const closeSModal = () => setSmodalOpen(false);


  const downloadChart = () => {
    const canvas = document.querySelector(".graph-container canvas") as HTMLCanvasElement | null;
  
    if (canvas) {
      const imageURL = canvas.toDataURL("image/png");
      const link = document.createElement("a");
      link.href = imageURL;
      link.download = `${chartTitle}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      console.error("Chart canvas not found!");
    }
  };
  

  const fetchData = async () => {
    try {
      const response = await fetch("http://localhost:8000/get_chart_data");
      if (!response.ok) {
        throw new Error("Failed to fetch data");
      }
      const data = await response.json();
      setListData(data.data);
    } catch (error: any) {
      console.error("Fetch error:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchData();
  }, [isOpen]);


  const handleRemoveGraph = async (timestamp: any) => {
    try {
      await removeGraph(timestamp);
      await fetchData();
    } catch (error) {
      console.error("Error removing graph:", error);
    }

    setSmodalOpen(false);
  };

  return (
    <div className="list-container">

      <Modal isOpen={isLModalOpen} onClose={closeModal}>
            <div className="modal-title">
              <h2><strong>{chartTitle}</strong>, Saved: {new Date(chartDate).toLocaleString()}</h2>
            </div>
            <ChartJs chartData={chartData} chartOptions={chartOptions} chartType={chartType}  />
            <div className="save-btn">
              <button onClick={downloadChart}>Download Chart</button>
            </div>
      </Modal> 

      <SmallDialog isOpen={isSmodalOpen} onClose={closeSModal}>
      <div className="modal-title">
              <h2><strong>Are you sure you want to delete?</strong></h2>
            </div>
            <div className="cfm-btn">
            <button onClick={() => handleRemoveGraph(chartDate)}>Yes</button>
            <button onClick={closeSModal}>No</button>
            </div>
      </SmallDialog>

        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p>Error: {error}</p>
        ) : (
          <div className='list-content'>
            {listData.length === 0 ? (
            <p>No archived graphs</p>
          ) : (
            <ul>
              {listData.map((chart, index) => (
                <li key={index}>
                      <h1>{(chart.title)}</h1>
                      <h3><strong>Saved on: </strong>{new Date(chart.date).toLocaleString()}</h3> 
                      <p>{(chart.description)}</p>

                      <div className='list-btns'>
                        <button onClick={() => openModal(chart.chartData, chart.chartType, chart.chartOptions, chart.title, chart.date)}> View </button>
                        <button onClick={() => openSmodal(chart.date)}>Remove</button>
                      </div>   
                  <hr className='dividers'/>
                </li>
              ))}
            </ul>
          )}
          </div>
        )}
    </div>
  );
};

export default Archived_Graphs_List;
