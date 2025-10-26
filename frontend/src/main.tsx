import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

// Error boundary wrapper
const ErrorBoundary = () => {
  return (
    <div>
      <App />
    </div>
  );
};

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found");
}

createRoot(rootElement).render(<ErrorBoundary />);
