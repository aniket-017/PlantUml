import React from 'react';
import { AppProvider } from './context/AppContext';
import { useApp } from './hooks/useApp';
import StepIndicator from './components/StepIndicator';
import FileUpload from './components/FileUpload';
import TestCaseEditor from './components/TestCaseEditor';
import DiagramViewer from './components/DiagramViewer';
import ChatInterface from './components/ChatInterface';
import './App.css';

const AppContent = () => {
  const { state } = useApp();

  const renderCurrentStep = () => {
    switch (state.currentStep) {
      case 'upload':
        return <FileUpload />;
      case 'edit':
        return <TestCaseEditor />;
      case 'diagram':
        return <DiagramViewer />;
      case 'chat':
        return <ChatInterface />;
      default:
        return <FileUpload />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <StepIndicator />
      <main className="py-8">
        {renderCurrentStep()}
      </main>
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
