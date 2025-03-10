const saveGraph = async (chartData: any, chartOptions: any, chartType: any, chartTitle: string, chartDescription: string) => {
    const timestamp = Date.now();
  
    const data = {
      chartData,       
      chartOptions,   
      chartType,       
      date: timestamp,
      title: chartTitle,
      description: chartDescription
    };
  
    try {
      const response = await fetch("http://localhost:8000/save_chart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
  
      const result = await response.json();
      console.log("Upload Success:", result);
    } catch (error) {
      console.error("Upload Error:", error);
    }
};

const removeGraph = async (id: number) => {
  try {
    const response = await fetch("http://localhost:8000/remove_saved_chart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({timestamp: id}),
    });
    const result = await response.json();
    console.log("Removal Success:", result);
  } catch (error) {
    console.error("Removal Error:", error);
  }

}


export {removeGraph, saveGraph}