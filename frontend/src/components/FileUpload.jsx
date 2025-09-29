import React, { useState, useEffect } from "react";
import { Upload, FileSpreadsheet, AlertCircle } from "lucide-react";
import { apiService } from "../services/api";
import { useApp } from "../hooks/useApp";
import { setLoading, setError, setTestCases, setUploadedFile, setStep, setApiKey } from "../context/actions";
import { storage } from "../utils/storage";
import LoadingSpinner from "./LoadingSpinner";

const FileUpload = () => {
  const { state, dispatch } = useApp();
  const [dragActive, setDragActive] = useState(false);

  // Check for API key on component mount
  useEffect(() => {
    const savedApiKey = storage.getValidatedApiKey();
    if (savedApiKey) {
      setApiKey(dispatch, savedApiKey);
      apiService.setApiKey(savedApiKey);
      setStep(dispatch, "upload");
    }
  }, [dispatch]);

  const handleFiles = async (files) => {
    if (!files || files.length === 0) return;

    const file = files[0];

    // Validate file type
    const validTypes = [
      "text/csv",
      "application/vnd.ms-excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx|xls)$/i)) {
      setError(dispatch, "Please select a CSV or Excel file");
      return;
    }

    try {
      setLoading(dispatch, true);
      const result = await apiService.uploadFile(file);

      if (result.success) {
        setUploadedFile(dispatch, file);
        setTestCases(dispatch, result.test_cases);
        setStep(dispatch, "edit");
      } else {
        setError(dispatch, "Failed to process file");
      }
    } catch (error) {
      setError(dispatch, error.message || "Failed to upload file");
    } finally {
      setLoading(dispatch, false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  if (state.loading) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-blue-900 via-blue-700 to-indigo-800 z-50 flex items-center justify-center">
        <LoadingSpinner type="testCases" text="AI is analyzing your file..." subText="This may take a few moments..." />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4 sm:p-6">
      <div className="text-center mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-4xl font-bold text-gray-800 mb-4">CSV to PlantUML Generator</h1>
        <p className="text-base sm:text-lg text-gray-600">
          Upload your CSV or Excel file to generate beautiful UML diagrams
        </p>
      </div>

      {state.error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
          <AlertCircle className="h-5 w-5 mr-2" />
          {state.error}
        </div>
      )}

      <div
        className={`relative border-2 border-dashed rounded-lg p-4 sm:p-8 text-center transition-colors ${
          dragActive ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-blue-400 hover:bg-blue-50"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          accept=".csv,.xlsx,.xls"
          onChange={handleChange}
          disabled={state.loading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />

        <div className="space-y-4">
          <Upload className="h-10 w-10 sm:h-12 sm:w-12 text-gray-400 mx-auto" />

          <div>
            <p className="text-base sm:text-lg font-medium text-gray-700">Drop your file here or click to browse</p>
            <p className="text-xs sm:text-sm text-gray-500 mt-1">Supports CSV and Excel files (.csv, .xlsx, .xls)</p>
          </div>

          <button
            type="button"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm sm:text-base"
            onClick={() => document.getElementById("file-upload").click()}
          >
            <FileSpreadsheet className="h-4 w-4 mr-2" />
            Choose File
          </button>
        </div>
      </div>

      <div className="mt-6 sm:mt-8 bg-gray-50 rounded-lg p-4 sm:p-6">
        <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3">How it works:</h3>
        <div className="space-y-2 text-xs sm:text-sm text-gray-600">
          <div className="flex items-center">
            <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold mr-3">
              1
            </span>
            Upload your CSV or Excel file containing test case data
          </div>
          <div className="flex items-center">
            <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold mr-3">
              2
            </span>
            Review and edit test cases if needed
          </div>
          <div className="flex items-center">
            <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold mr-3">
              3
            </span>
            Generate your PlantUML diagram automatically
          </div>
          <div className="flex items-center">
            <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold mr-3">
              4
            </span>
            Refine the diagram using our AI chat interface
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
