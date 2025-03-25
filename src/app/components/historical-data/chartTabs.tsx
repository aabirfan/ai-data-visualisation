"use client"
import React, { useState } from "react";
import {LLMCharts} from "./ai-charts/llmCharts"
import ManualCharts from "./manual-charts/manualCharts"

import '../../styles/chartsTabs.css'; 

type ChartTabsProps = {
    selectedAsset: string | null; 
  };


export default function ChartTabs({selectedAsset}: ChartTabsProps) {

    const [activeTab, setActiveTab] = useState<string>("AI");
    const [loading, setLoading] = useState<boolean>(false); 

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
            {activeTab === 'AI' && <LLMCharts loading={loading} setLoading={setLoading} selectedAsset={selectedAsset}/>}
            {activeTab === 'Manual' && <ManualCharts />}
         </div>
    ); 
  }