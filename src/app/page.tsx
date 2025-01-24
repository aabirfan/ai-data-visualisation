import Image from "next/image";
import React from "react";
import ChartTabs from "./components/historical-data/chartTabs"


export default function Home() {

    return (
      <>
    <header>
       <Image
          className="logo"
          alt="Twilligent logo"
          src="/logo.png"
          width={300}
          height={300}
          loading="lazy"
        />
    </header>
    <main>
        <ChartTabs />
    </main>
     </>
    );
  }

