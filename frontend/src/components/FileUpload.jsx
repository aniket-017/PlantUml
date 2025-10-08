import React, { useState, useEffect } from "react";
import { Upload, FileSpreadsheet, Database, AlertCircle } from "lucide-react";
import { apiService } from "../services/api";
import { useApp } from "../hooks/useApp";
import {
  setLoading,
  setError,
  setTestCases,
  setCmdbItems,
  setUploadedFile,
  setStep,
  setApiKey,
} from "../context/actions";
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
    const fileType = state.fileType || "test-cases";

    // Validate file type based on selected file type
    let validTypes, validExtensions, errorMessage;

    if (fileType === "cmdb") {
      validTypes = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/json",
        "text/yaml",
        "application/x-yaml",
      ];
      validExtensions = /\.(csv|xlsx|xls|json|yaml|yml)$/i;
      errorMessage = "Please select a CSV, Excel, JSON, or YAML file for CMDB data";
    } else {
      validTypes = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      ];
      validExtensions = /\.(csv|xlsx|xls)$/i;
      errorMessage = "Please select a CSV or Excel file for test cases";
    }

    if (!validTypes.includes(file.type) && !file.name.match(validExtensions)) {
      setError(dispatch, errorMessage);
      return;
    }

    try {
      setLoading(dispatch, true);
      const result = await apiService.uploadFile(file, fileType);

      if (result.success) {
        setUploadedFile(dispatch, file);

        if (fileType === "cmdb") {
          setCmdbItems(dispatch, result.cmdb_items);
        } else {
          setTestCases(dispatch, result.test_cases);
        }

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
    const fileType = state.fileType || "test-cases";
    const loadingText =
      fileType === "cmdb" ? "AI is analyzing your CMDB data..." : "AI is analyzing your test cases...";
    const subText =
      fileType === "cmdb"
        ? "Processing infrastructure components and relationships..."
        : "This may take a few moments...";

    return (
      <div className="fixed inset-0 bg-gradient-to-br from-blue-900 via-blue-700 to-indigo-800 z-50 flex items-center justify-center">
        <LoadingSpinner type={fileType} text={loadingText} subText={subText} />
      </div>
    );
  }

  const fileType = state.fileType || "test-cases";
  const isCmdb = fileType === "cmdb";
  const title = isCmdb ? "CMDB to PlantUML Generator" : "Test Cases to PlantUML Generator";
  const description = isCmdb
    ? "Upload your CMDB file to generate system architecture diagrams"
    : "Upload your CSV or Excel file to generate test flow diagrams";
  const supportedFormats = isCmdb
    ? "CSV, Excel, JSON, YAML files (.csv, .xlsx, .json, .yaml)"
    : "CSV and Excel files (.csv, .xlsx, .xls)";
  const Icon = isCmdb ? Database : FileSpreadsheet;

  return (
    <div className="max-w-2xl mx-auto p-4 sm:p-6">
      <div className="text-center mb-6 sm:mb-8">
        <div className="flex items-center justify-center mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center mr-3">
            <Icon className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-bold text-gray-800">{title}</h1>
        </div>
        <p className="text-base sm:text-lg text-gray-600">{description}</p>
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
          accept={isCmdb ? ".csv,.xlsx,.xls,.json,.yaml,.yml" : ".csv,.xlsx,.xls"}
          onChange={handleChange}
          disabled={state.loading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />

        <div className="space-y-4">
          <Upload className="h-10 w-10 sm:h-12 sm:w-12 text-gray-400 mx-auto" />

          <div>
            <p className="text-base sm:text-lg font-medium text-gray-700">Drop your file here or click to browse</p>
            <p className="text-xs sm:text-sm text-gray-500 mt-1">Supports {supportedFormats}</p>
          </div>

          <button
            type="button"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm sm:text-base"
            onClick={() => document.getElementById("file-upload").click()}
          >
            <Icon className="h-4 w-4 mr-2" />
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
            {isCmdb
              ? "Upload your CMDB file containing system configuration data"
              : "Upload your CSV or Excel file containing test case data"}
          </div>
          <div className="flex items-center">
            <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold mr-3">
              2
            </span>
            {isCmdb ? "Review and edit CMDB items and relationships if needed" : "Review and edit test cases if needed"}
          </div>
          <div className="flex items-center">
            <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold mr-3">
              3
            </span>
            {isCmdb
              ? "Generate your system architecture PlantUML diagram automatically"
              : "Generate your PlantUML diagram automatically"}
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
