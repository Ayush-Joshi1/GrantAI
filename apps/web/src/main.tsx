import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import { App } from "@/app/App";
import "@/styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3500,
          style: {
            background: "rgba(2, 6, 23, 0.72)",
            color: "rgba(248, 250, 252, 0.95)",
            border: "1px solid rgba(148, 163, 184, 0.18)",
            backdropFilter: "blur(16px)"
          }
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
);

