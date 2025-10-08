import React, { useState } from "react";
import { ArrowLeft, MessageCircle, Download, Code, Copy, Check } from "lucide-react";
import { useApp } from "../hooks/useApp";
import { setStep } from "../context/actions";
import { apiService } from "../services/api";

const DiagramViewer = () => {
  const { state, dispatch } = useApp();
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(state.plantUMLCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  const handleDownload = async () => {
    if (state.plantUMLImage) {
      setDownloading(true);
      try {
        const imageUrl = apiService.getImageUrl(state.plantUMLImage);

        // Fetch the image as a blob
        const response = await fetch(imageUrl);
        if (!response.ok) {
          throw new Error("Failed to fetch image");
        }

        const blob = await response.blob();

        // Create a blob URL and download
        const blobUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = blobUrl;
        link.download = `diagram_${new Date().toISOString().split("T")[0]}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up the blob URL
        window.URL.revokeObjectURL(blobUrl);
      } catch (error) {
        console.error("Download failed:", error);
        // Fallback: try to open in new tab
        const imageUrl = apiService.getImageUrl(state.plantUMLImage);
        window.open(imageUrl, "_blank");
      } finally {
        setDownloading(false);
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">
            {state.fileType === "cmdb" ? "System Architecture Diagram" : "Generated Diagram"}
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">
            {state.fileType === "cmdb"
              ? "Your system architecture diagram is ready! You can refine it using the chat interface."
              : "Your PlantUML diagram is ready! You can refine it using the chat interface."}
          </p>
        </div>
        <button
          onClick={() => setStep(dispatch, "edit")}
          className="flex items-center justify-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Edit
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Diagram Display */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-2 sm:space-y-0">
                <h2 className="text-base sm:text-lg font-semibold text-gray-800">Diagram</h2>
                <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                  <button
                    onClick={handleDownload}
                    disabled={downloading}
                    className="flex items-center justify-center px-3 py-1 text-xs sm:text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {downloading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1"></div>
                        Downloading...
                      </>
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => setShowCode(!showCode)}
                    className="flex items-center justify-center px-3 py-1 text-xs sm:text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    <Code className="h-4 w-4 mr-1" />
                    {showCode ? "Hide Code" : "Show Code"}
                  </button>
                </div>
              </div>
            </div>

            <div className="p-4 sm:p-6">
              {state.plantUMLImage ? (
                <div className="text-center">
                  <img
                    key={`diagram-${Date.now()}-${state.plantUMLImage}`}
                    src={`${apiService.getImageUrl(state.plantUMLImage)}?t=${Date.now()}`}
                    alt="Generated PlantUML Diagram"
                    className="max-w-full h-auto mx-auto border border-gray-200 rounded-lg shadow-sm"
                    onError={(e) => {
                      e.target.style.display = "none";
                      e.target.nextSibling.style.display = "block";
                    }}
                  />
                  <div style={{ display: "none" }} className="text-red-500 p-4">
                    Failed to load diagram image
                  </div>
                  <div className="mt-2 text-xs text-gray-500">Generated: {new Date().toLocaleString()}</div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <p>No diagram available</p>
                </div>
              )}

              {showCode && state.plantUMLCode && (
                <div className="mt-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-gray-700">PlantUML Code</h3>
                    <button
                      onClick={handleCopyCode}
                      className="flex items-center px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      {copied ? (
                        <>
                          <Check className="h-3 w-3 mr-1" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3 mr-1" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <pre className="bg-gray-50 p-4 rounded-md text-sm overflow-x-auto border">
                    <code>{state.plantUMLCode}</code>
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Action Panel */}
        <div className="space-y-4 sm:space-y-6">
          <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
            <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-4">Next Steps</h3>
            <div className="space-y-3">
              <button
                onClick={() => setStep(dispatch, "chat")}
                className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Refine with AI Chat
              </button>

              <button
                onClick={() => setStep(dispatch, "edit")}
                className="w-full flex items-center justify-center px-4 py-3 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                {state.fileType === "cmdb" ? "Edit CMDB Items" : "Edit Test Cases"}
              </button>

              <button
                onClick={() => setStep(dispatch, "upload")}
                className="w-full flex items-center justify-center px-4 py-3 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                Upload New File
              </button>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4 sm:p-6">
            <h4 className="font-semibold text-blue-800 mb-2 text-sm sm:text-base">💡 Pro Tips</h4>
            <div className="space-y-2 text-xs sm:text-sm text-blue-700">
              <p>• Use the chat interface to add actors, modify flows, or adjust the diagram structure</p>
              <p>• Download the image for presentations or documentation</p>
              <p>• Copy the PlantUML code to use in other tools</p>
            </div>
          </div>

          {(state.testCases.length > 0 || state.cmdbItems.length > 0) && (
            <div className="bg-gray-50 rounded-lg p-4 sm:p-6">
              <h4 className="font-semibold text-gray-800 mb-2 text-sm sm:text-base">
                {state.fileType === "cmdb" ? "CMDB Items Summary" : "Test Cases Summary"}
              </h4>
              <div className="text-xs sm:text-sm text-gray-600">
                <p>
                  {state.fileType === "cmdb"
                    ? `Total CMDB items: ${state.cmdbItems.length}`
                    : `Total test cases: ${state.testCases.length}`}
                </p>
                <p>
                  File: <span className="font-medium">{state.uploadedFile?.name}</span>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DiagramViewer;
