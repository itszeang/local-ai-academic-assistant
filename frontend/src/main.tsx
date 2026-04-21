import React from "react";
import ReactDOM from "react-dom/client";

import { WorkspacePage } from "./pages/WorkspacePage";
import "./styles/academic-workspace.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <WorkspacePage />
  </React.StrictMode>
);
