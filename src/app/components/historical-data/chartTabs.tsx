"use client"
import React, { useState } from "react";
import '../styles/chartsTabs.css'; 
import LLMCharts from "./llmCharts"
import ManualCharts from "./manualCharts"

export default function chartTabs() {

    const [activeTab, setActiveTab] = useState("AI");

    return(
        <div className="charts-container">
            <div className="tab-row">
                 <div className={activeTab === 'AI' ? 'active-row' : 'row'}>
                     <button className={activeTab === "AI" ? "active-tab-btn" : "tab-btn"} onClick={() => setActiveTab("AI")}>GenAI Charts</button>
                </div>
                <div className={activeTab === 'Manual' ? 'active-row' : 'row'}>
                    <button className={activeTab === "Manual" ? "active-tab-btn" : "tab-btn"} onClick={() => setActiveTab("Manual")}>Manual Charts</button>
                </div>
            </div>
            {activeTab === 'AI' && <LLMCharts />}
            {activeTab === 'Manual' && <ManualCharts />}
         </div>
    ); 
  }