import { Navigate, createBrowserRouter } from "react-router-dom";
import { App } from "./App";
import { AssetsPage } from "../pages/AssetsPage";
import { RoomPage } from "../pages/RoomPage";
import { WorkspacePage } from "../pages/WorkspacePage";
import { CompanyPage } from "../pages/CompanyPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Navigate to="/workspace" replace /> },
      { path: "workspace", element: <WorkspacePage /> },
      { path: "rooms/:roomId", element: <RoomPage /> },
      { path: "assets", element: <AssetsPage /> },
      { path: "company", element: <CompanyPage /> },
    ],
  },
]);
