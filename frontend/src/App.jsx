import React from "react";
import { AppProvider } from "./context/AppContext";
import { useApp } from "./hooks/useApp";
import { setApiKey, setStep } from "./context/actions";
import { apiService } from "./services/api";
import LandingPage from "./components/LandingPage";
import StepIndicator from "./components/StepIndicator";
import ApiKeyInput from "./components/ApiKeyInput";
import FileUpload from "./components/FileUpload";
import TestCaseEditor from "./components/TestCaseEditor";
import DiagramViewer from "./components/DiagramViewer";
import ChatInterface from "./components/ChatInterface";
import "./App.css";

const AppContent = () => {
  const { state, dispatch } = useApp();

  const handleApiKeySet = (apiKey) => {
    // Set API key in context and API service
    setApiKey(dispatch, apiKey);
    apiService.setApiKey(apiKey);
    setStep(dispatch, "upload");
  };

  const renderCurrentStep = () => {
    switch (state.currentStep) {
      case "landing":
        return <LandingPage />;
      case "api-key":
        return <ApiKeyInput onApiKeySet={handleApiKeySet} />;
      case "upload":
        return <FileUpload />;
      case "edit":
        return <TestCaseEditor />;
      case "diagram":
        return <DiagramViewer />;
      case "chat":
        return <ChatInterface />;
      default:
        return <LandingPage />;
    }
  };

  return (
    <div className="min-h-screen">
      <StepIndicator />
      <main className={state.currentStep === "landing" ? "" : "py-8 bg-gray-50"}>{renderCurrentStep()}</main>
    </div>
  );
};

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
