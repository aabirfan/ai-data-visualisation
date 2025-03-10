"use client"
import React, { useState } from "react";
import {LLMCharts} from "./ai-charts/llmCharts"
import ManualCharts from "./manual-charts/manualCharts"

import '../../styles/chartsTabs.css'; 


export default function ChartTabs() {

    const [activeTab, setActiveTab] = useState("AI");
    const [loading, setLoading] = useState(false); 

    return(
        <div className="charts-container">
            <div className="tab-row">
                 <div className={activeTab === 'AI' ? 'active-row' : 'row'}>
                     <button className={activeTab === "AI" ? "active-tab-btn" : "tab-btn"} onClick={() => setActiveTab("AI")}>illi Charts</button>
                </div>
                <div className={activeTab === 'Manual' ? 'active-row' : 'row'}>
                    <button className={activeTab === "Manual" ? "active-tab-btn" : "tab-btn"} onClick={() => setActiveTab("Manual")}>Manual Charts</button>
                </div>
            </div>
            {activeTab === 'AI' && <LLMCharts loading={loading} setLoading={setLoading}/>}
            {activeTab === 'Manual' && <ManualCharts />}
         </div>
    ); 
  }