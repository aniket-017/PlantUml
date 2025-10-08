import React from "react";
import { Key, FileText, Upload, Edit, Image, MessageCircle, Check } from "lucide-react";
import { useApp } from "../hooks/useApp";

const StepIndicator = () => {
  const { state } = useApp();

  // Don't show step indicator on landing page
  if (state.currentStep === "landing") {
    return null;
  }

  const steps = [
    {
      id: "api-key",
      title: "API Key",
      icon: Key,
      description: "Enter OpenAI API key",
    },
    {
      id: "file-type",
      title: "File Type",
      icon: FileText,
      description: "Choose test cases or CMDB",
    },
    {
      id: "upload",
      title: "Upload File",
      icon: Upload,
      description: state.fileType === "cmdb" ? "Upload CMDB file" : "Upload CSV or Excel file",
    },
    {
      id: "edit",
      title: state.fileType === "cmdb" ? "Edit CMDB Items" : "Edit Test Cases",
      icon: Edit,
      description: state.fileType === "cmdb" ? "Review and modify CMDB items" : "Review and modify test cases",
    },
    {
      id: "diagram",
      title: "View Diagram",
      icon: Image,
      description: "Generated PlantUML diagram",
    },
    {
      id: "chat",
      title: "Refine with AI",
      icon: MessageCircle,
      description: "Chat to improve diagram",
    },
  ];

  const getStepStatus = (stepId) => {
    const currentIndex = steps.findIndex((step) => step.id === state.currentStep);
    const stepIndex = steps.findIndex((step) => step.id === stepId);

    if (stepIndex < currentIndex) return "completed";
    if (stepIndex === currentIndex) return "current";
    return "upcoming";
  };

  const getProgressPercentage = () => {
    const currentIndex = steps.findIndex((step) => step.id === state.currentStep);
    // Progress should be 0% for first step, then incrementally increase
    // First step (index 0) = 0%, second step (index 1) = 20%, etc.
    return (currentIndex / steps.length) * 100;
  };

  return (
    <div className="bg-gradient-to-r from-slate-50 to-blue-50 border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span className="font-medium">Progress</span>
            <span className="font-medium">{Math.round(getProgressPercentage())}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-700 ease-out progress-fill-animated"
              style={{
                width: `${getProgressPercentage()}%`,
                "--progress-width": `${getProgressPercentage()}%`,
              }}
            />
          </div>
        </div>

        <nav aria-label="Progress">
          {/* Mobile: Vertical layout */}
          <div className="block lg:hidden">
            <ol className="space-y-8">
              {steps.map((step, stepIdx) => {
                const status = getStepStatus(step.id);
                const Icon = step.icon;

                return (
                  <li
                    key={step.id}
                    className="flex items-start step-slide-in"
                    style={{ animationDelay: `${stepIdx * 0.1}s` }}
                  >
                    <div className="relative flex items-center justify-center mr-6">
                      <div
                        className={`flex h-14 w-14 items-center justify-center rounded-full border-3 transition-all duration-300 ${
                          status === "completed"
                            ? "bg-gradient-to-r from-green-500 to-emerald-500 border-green-500 shadow-lg shadow-green-200 step-glow"
                            : status === "current"
                            ? "border-blue-500 bg-white shadow-lg shadow-blue-200 step-pulse"
                            : "border-gray-300 bg-white"
                        }`}
                      >
                        {status === "completed" ? (
                          <Check className="h-7 w-7 text-white animate-bounce" />
                        ) : (
                          <Icon className={`h-7 w-7 ${status === "current" ? "text-blue-500" : "text-gray-400"}`} />
                        )}
                      </div>
                      {/* Mobile connector */}
                      {stepIdx !== steps.length - 1 && (
                        <div
                          className="absolute top-14 left-1/2 transform -translate-x-1/2 w-1 h-10 rounded-full transition-all duration-500 connector-draw"
                          style={{
                            backgroundColor:
                              getStepStatus(steps[stepIdx + 1].id) !== "upcoming" ? "#10b981" : "#d1d5db",
                          }}
                        />
                      )}
                    </div>

                    <div className="flex-1 min-w-0 pt-2">
                      <div
                        className={`text-lg font-semibold transition-colors duration-300 ${
                          status === "current"
                            ? "text-blue-600"
                            : status === "completed"
                            ? "text-gray-900"
                            : "text-gray-500"
                        }`}
                      >
                        {step.title}
                      </div>
                      <div className="text-sm text-gray-600 mt-2 leading-relaxed">{step.description}</div>
                      {status === "current" && (
                        <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full text-xs text-blue-600 bg-blue-50 font-medium animate-pulse">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
                          Current Step
                        </div>
                      )}
                      {status === "completed" && (
                        <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full text-xs text-green-600 bg-green-50 font-medium">
                          <Check className="w-3 h-3 mr-2" />
                          Completed
                        </div>
                      )}
                    </div>
                  </li>
                );
              })}
            </ol>
          </div>

          {/* Desktop: Horizontal layout */}
          <div className="hidden lg:block">
            <ol className="flex items-center justify-between">
              {steps.map((step, stepIdx) => {
                const status = getStepStatus(step.id);
                const Icon = step.icon;

                return (
                  <li
                    key={step.id}
                    className="relative flex-1 group step-slide-in"
                    style={{ animationDelay: `${stepIdx * 0.1}s` }}
                  >
                    <div
                      className={`flex flex-col items-center ${stepIdx !== steps.length - 1 ? "pr-8 xl:pr-20" : ""}`}
                    >
                      <div className="relative flex items-center justify-center mb-4">
                        <div
                          className={`flex h-16 w-16 items-center justify-center rounded-full border-3 transition-all duration-300 group-hover:scale-110 ${
                            status === "completed"
                              ? "bg-gradient-to-r from-green-500 to-emerald-500 border-green-500 shadow-lg shadow-green-200 step-glow"
                              : status === "current"
                              ? "border-blue-500 bg-white shadow-lg shadow-blue-200 step-pulse"
                              : "border-gray-300 bg-white group-hover:border-blue-300 group-hover:shadow-md"
                          }`}
                        >
                          {status === "completed" ? (
                            <Check className="h-8 w-8 text-white animate-bounce" />
                          ) : (
                            <Icon
                              className={`h-8 w-8 ${
                                status === "current" ? "text-blue-500" : "text-gray-400 group-hover:text-blue-400"
                              }`}
                            />
                          )}
                        </div>
                      </div>

                      <div className="text-center">
                        <div
                          className={`text-base font-bold transition-colors duration-300 ${
                            status === "current"
                              ? "text-blue-600"
                              : status === "completed"
                              ? "text-gray-900"
                              : "text-gray-500 group-hover:text-gray-700"
                          }`}
                        >
                          {step.title}
                        </div>
                        <div className="text-sm text-gray-600 mt-2 max-w-32 leading-tight">{step.description}</div>
                        {status === "current" && (
                          <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full text-xs text-blue-600 bg-blue-50 font-medium animate-pulse">
                            <div className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
                            Current
                          </div>
                        )}
                        {status === "completed" && (
                          <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full text-xs text-green-600 bg-green-50 font-medium">
                            <Check className="w-3 h-3 mr-2" />
                            Done
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Desktop connector */}
                    {stepIdx !== steps.length - 1 && (
                      <div
                        className="absolute top-8 right-0 hidden h-1 w-8 xl:w-20 xl:block rounded-full transition-all duration-500 connector-draw"
                        style={{
                          backgroundColor: getStepStatus(steps[stepIdx + 1].id) !== "upcoming" ? "#10b981" : "#d1d5db",
                        }}
                      />
                    )}
                  </li>
                );
              })}
            </ol>
          </div>
        </nav>
      </div>
    </div>
  );
};

export default StepIndicator;
