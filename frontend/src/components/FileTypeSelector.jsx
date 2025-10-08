import React from "react";
import { FileText, Database, ArrowRight } from "lucide-react";
import { useApp } from "../hooks/useApp";
import { setFileType, setStep } from "../context/actions";

const FileTypeSelector = () => {
  const { dispatch } = useApp();

  const handleFileTypeSelect = (fileType) => {
    setFileType(dispatch, fileType);
    setStep(dispatch, "upload");
  };

  const fileTypes = [
    {
      id: "test-cases",
      title: "Test Cases",
      description: "Upload CSV or Excel files containing test case data to generate test flow diagrams",
      icon: FileText,
      features: [
        "Test case analysis",
        "Test flow visualization",
        "Step-by-step process mapping",
        "Test scenario documentation",
      ],
      supportedFormats: "CSV, Excel (.csv, .xlsx, .xls)",
    },
    {
      id: "cmdb",
      title: "CMDB (Configuration Management Database)",
      description: "Upload CMDB files to generate system architecture and infrastructure diagrams",
      icon: Database,
      features: [
        "System architecture mapping",
        "Component relationship analysis",
        "Infrastructure visualization",
        "Dependency tracking",
      ],
      supportedFormats: "CSV, Excel, JSON, YAML (.csv, .xlsx, .json, .yaml)",
    },
  ];

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-4">Choose Your File Type</h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Select the type of data you want to visualize. Our AI will generate appropriate diagrams based on your
          selection.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {fileTypes.map((fileType) => {
          const Icon = fileType.icon;
          return (
            <div
              key={fileType.id}
              className="group relative bg-white rounded-2xl border-2 border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all duration-300 overflow-hidden"
            >
              <div className="p-8">
                <div className="flex items-center mb-6">
                  <div className="flex-shrink-0 w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                    <Icon className="h-8 w-8 text-white" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-2xl font-bold text-gray-900">{fileType.title}</h3>
                    <p className="text-sm text-blue-600 font-medium">Supported formats: {fileType.supportedFormats}</p>
                  </div>
                </div>

                <p className="text-gray-600 mb-6 leading-relaxed">{fileType.description}</p>

                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-gray-800 mb-3">Key Features:</h4>
                  <ul className="space-y-2">
                    {fileType.features.map((feature, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-600">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handleFileTypeSelect(fileType.id)}
                  className="w-full group/btn inline-flex items-center justify-center px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  Select {fileType.title}
                  <ArrowRight className="ml-2 h-5 w-5 group-hover/btn:translate-x-1 transition-transform duration-200" />
                </button>
              </div>

              {/* Hover effect overlay */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            </div>
          );
        })}
      </div>

      <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8">
        <div className="text-center">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Not sure which option to choose?</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Choose Test Cases if you have:</h4>
              <ul className="space-y-1">
                <li>• Test case spreadsheets</li>
                <li>• Test execution data</li>
                <li>• QA process documentation</li>
                <li>• Test scenario descriptions</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Choose CMDB if you have:</h4>
              <ul className="space-y-1">
                <li>• System configuration data</li>
                <li>• Infrastructure components</li>
                <li>• Service dependencies</li>
                <li>• Asset management data</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileTypeSelector;
