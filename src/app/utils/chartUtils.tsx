export const handleChartRequest = async (
    query: string | number[],
    setLoading: React.Dispatch<React.SetStateAction<boolean>>,
    setResponse: React.Dispatch<React.SetStateAction<any>>,
    setChartData: React.Dispatch<React.SetStateAction<any>>,
    setChartOptions: React.Dispatch<React.SetStateAction<any>>,
    setChartType: React.Dispatch<React.SetStateAction<any>>
  ) => {
    setLoading(true);
    setResponse(null);
  
    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
  
      let data;
      try {
        data = await res.json();
      } catch (error) {
        console.error("Invalid JSON response:", error);
        data = { error: "Invalid response from server." };
      }
  
      if (!res.ok) {
        setResponse({ error: "Unexpected error occurred." });
      } else {
        if (typeof data.message === "string") {
          data.message = data.message.replace(/```typescript|```|json/g, "");
        }
  
        setResponse(data);
        console.log("API Response:", data.message);
  
        try {
          const parsedCode = JSON.parse(data.message);
          setChartData(parsedCode.data);
          setChartOptions(parsedCode.options);
  
          if (parsedCode.data?.type) {
            setChartType(parsedCode.data.type);
          }
        } catch (error) {
          console.error("Error parsing chart data:", error);
        }
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setResponse({ error: "An error occurred while processing your request." });
    } finally {
      setLoading(false);
    }
  };
  