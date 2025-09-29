import React, { useState } from "react";
import {
  Edit2,
  ArrowLeft,
  ArrowRight,
  AlertCircle,
  FileText,
  CheckCircle,
  Target,
  List,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { useApp } from "../hooks/useApp";
import { updateTestCase, setStep, setLoading, setError, setPlantUMLData } from "../context/actions";
import { apiService } from "../services/api";
import LoadingSpinner from "./LoadingSpinner";

const TestCaseEditor = () => {
  const { state, dispatch } = useApp();
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [expandedIds, setExpandedIds] = useState([]);

  // Parse JSON action data safely
  const parseActionData = (action) => {
    try {
      if (typeof action === "string") {
        return JSON.parse(action);
      }
      return action;
    } catch {
      return { Steps: action || "No steps provided" };
    }
  };

  const handleEdit = (testCase) => {
    setEditingId(testCase.id);
    setEditForm({
      title: testCase.title,
      expected: testCase.expected || "",
      description: testCase.description || "",
    });
  };

  const handleSave = () => {
    updateTestCase(dispatch, editingId, editForm);
    setEditingId(null);
    setEditForm({});
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditForm({});
  };

  const toggleExpand = (testCaseId) => {
    setExpandedIds((prev) =>
      prev.includes(testCaseId) ? prev.filter((id) => id !== testCaseId) : [...prev, testCaseId]
    );
  };

  const handleGenerateDiagram = async () => {
    try {
      setLoading(dispatch, true);
      const result = await apiService.generateDiagram(state.testCases);

      if (result.success) {
        setPlantUMLData(dispatch, result.plantuml_code, result.plantuml_image);
        setStep(dispatch, "diagram");
      } else {
        setError(dispatch, "Failed to generate diagram");
      }
    } catch (error) {
      setError(dispatch, error.message || "Failed to generate diagram");
    } finally {
      setLoading(dispatch, false);
    }
  };

  if (state.loading) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 z-50 flex items-center justify-center">
        <LoadingSpinner type="flowchart" text="Generating Flowchart" subText="AI is building your diagram..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Edit Test Cases
            </h1>
            <p className="text-sm sm:text-base text-gray-600 mt-2">
              Review and modify your test cases before generating the diagram
            </p>
          </div>
          <button
            onClick={() => setStep(dispatch, "upload")}
            className="flex items-center justify-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-all border-2 border-gray-300 rounded-lg hover:bg-white hover:shadow-md"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Upload
          </button>
        </div>

        {state.error && (
          <div className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-lg flex items-center text-red-700 shadow-md">
            <AlertCircle className="h-5 w-5 mr-2" />
            {state.error}
          </div>
        )}

        {/* Summary Bar */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border-2 border-blue-100">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-800">
                  {state.testCases.length} Test Case{state.testCases.length !== 1 ? "s" : ""}
                </h2>
                <p className="text-sm text-gray-500">
                  {expandedIds.length > 0
                    ? `${expandedIds.length} expanded • Click to view details`
                    : "Click test cases to view details"}
                </p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => {
                  if (expandedIds.length === state.testCases.length) {
                    setExpandedIds([]);
                  } else {
                    setExpandedIds(state.testCases.map((tc) => tc.id));
                  }
                }}
                className="flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
              >
                {expandedIds.length === state.testCases.length ? (
                  <>
                    <ChevronRight className="h-4 w-4 mr-2" />
                    Collapse All
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4 mr-2" />
                    Expand All
                  </>
                )}
              </button>
              <button
                onClick={handleGenerateDiagram}
                disabled={state.loading || state.testCases.length === 0}
                className="flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 text-base font-semibold"
              >
                {state.loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <ArrowRight className="h-5 w-5 mr-2" />
                    Generate Diagram
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Test Cases Grid */}
        {state.testCases.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No test cases found. Please upload a valid file.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {state.testCases.map((testCase, index) => (
              <div
                key={testCase.id}
                className="bg-white rounded-xl shadow-lg border-2 border-gray-100 overflow-hidden hover:shadow-xl transition-all duration-300"
              >
                {editingId === testCase.id ? (
                  <div className="p-6">
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Title</label>
                        <input
                          type="text"
                          value={editForm.title}
                          onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Test case title"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Description</label>
                        <textarea
                          value={editForm.description}
                          onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                          rows={3}
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Test case description"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Expected Result</label>
                        <textarea
                          value={editForm.expected}
                          onChange={(e) => setEditForm({ ...editForm, expected: e.target.value })}
                          rows={2}
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Expected result"
                        />
                      </div>

                      <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 pt-4">
                        <button
                          onClick={handleSave}
                          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold shadow-md"
                        >
                          Save Changes
                        </button>
                        <button
                          onClick={handleCancel}
                          className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-semibold shadow-md"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <>
                    {/* Card Header - Always Visible */}
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 cursor-pointer hover:from-blue-600 hover:to-purple-700 transition-all"
                      onClick={() => toggleExpand(testCase.id)}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between space-y-3 sm:space-y-0">
                        <div className="flex-1 flex items-center">
                          <div className="mr-3">
                            {expandedIds.includes(testCase.id) ? (
                              <ChevronDown className="h-6 w-6 text-white" />
                            ) : (
                              <ChevronRight className="h-6 w-6 text-white" />
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center mb-2">
                              <div className="bg-white bg-opacity-30 rounded-lg px-3 py-1 mr-3">
                                <span className="text-white font-bold text-sm">#{index + 1}</span>
                              </div>
                              <h3 className="text-xl font-bold text-white">{testCase.title}</h3>
                            </div>
                            <p className="text-blue-100 text-sm font-medium">ID: {testCase.id}</p>
                          </div>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEdit(testCase);
                          }}
                          className="flex items-center justify-center px-4 py-2 bg-white text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-semibold shadow-lg"
                        >
                          <Edit2 className="h-4 w-4 mr-2" />
                          Edit
                        </button>
                      </div>
                    </div>

                    {/* Card Body - Only visible when expanded */}
                    {expandedIds.includes(testCase.id) && (
                      <div className="p-6 animate-[slideDown_0.3s_ease-out]">
                        {testCase.description && (
                          <div className="mb-6 p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500">
                            <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                              <FileText className="h-4 w-4 mr-2 text-blue-600" />
                              Description
                            </p>
                            <p className="text-gray-700">{testCase.description}</p>
                          </div>
                        )}

                        {testCase.steps && testCase.steps.length > 0 && (
                          <div className="space-y-4">
                            {testCase.steps.map((step, stepIndex) => {
                              const actionData = parseActionData(step.action);
                              return (
                                <div
                                  key={stepIndex}
                                  className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 border-2 border-blue-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-all"
                                >
                                  <div className="space-y-4">
                                    {/* Test Case ID & Scenario Row */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                      {actionData["Test Case ID"] && (
                                        <div className="bg-white rounded-lg p-3 shadow-sm">
                                          <span className="text-xs font-bold text-blue-600 uppercase tracking-wide flex items-center mb-1">
                                            <CheckCircle className="h-3 w-3 mr-1" />
                                            Test Case ID
                                          </span>
                                          <p className="text-base text-gray-800 font-semibold">
                                            {actionData["Test Case ID"]}
                                          </p>
                                        </div>
                                      )}

                                      {actionData["Scenario"] && (
                                        <div className="bg-white rounded-lg p-3 shadow-sm">
                                          <span className="text-xs font-bold text-green-600 uppercase tracking-wide flex items-center mb-1">
                                            <Target className="h-3 w-3 mr-1" />
                                            Scenario
                                          </span>
                                          <p className="text-base text-gray-800 font-medium">
                                            {actionData["Scenario"]}
                                          </p>
                                        </div>
                                      )}
                                    </div>

                                    {/* Preconditions */}
                                    {actionData["Preconditions"] && (
                                      <div className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-orange-400">
                                        <span className="text-xs font-bold text-orange-600 uppercase tracking-wide mb-2 block">
                                          Preconditions
                                        </span>
                                        <p className="text-sm text-gray-700 leading-relaxed">
                                          {actionData["Preconditions"]}
                                        </p>
                                      </div>
                                    )}

                                    {/* Steps */}
                                    {actionData["Steps"] && (
                                      <div className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-purple-400">
                                        <span className="text-xs font-bold text-purple-600 uppercase tracking-wide mb-3 flex items-center">
                                          <List className="h-4 w-4 mr-1" />
                                          Steps
                                        </span>
                                        <div className="space-y-2">
                                          {actionData["Steps"]
                                            .split(/\d+\./)
                                            .filter((stepText) => stepText.trim())
                                            .map((stepText, stepIdx) => (
                                              <div key={stepIdx} className="flex items-start group">
                                                <span className="flex-shrink-0 w-7 h-7 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center font-bold text-sm mr-3 group-hover:bg-purple-200 transition-colors">
                                                  {stepIdx + 1}
                                                </span>
                                                <span className="text-sm text-gray-700 pt-1 leading-relaxed">
                                                  {stepText.trim()}
                                                </span>
                                              </div>
                                            ))}
                                        </div>
                                      </div>
                                    )}

                                    {/* Expected Result */}
                                    {actionData["Expected Result"] && (
                                      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 shadow-sm border-2 border-green-300">
                                        <span className="text-xs font-bold text-green-700 uppercase tracking-wide mb-2 flex items-center">
                                          <CheckCircle className="h-4 w-4 mr-1" />
                                          Expected Result
                                        </span>
                                        <p className="text-sm text-gray-800 font-medium leading-relaxed">
                                          {actionData["Expected Result"]}
                                        </p>
                                      </div>
                                    )}

                                    {/* Remarks */}
                                    {actionData["Remarks"] && (
                                      <div className="bg-gray-50 rounded-lg p-4 shadow-sm border-l-4 border-gray-400">
                                        <span className="text-xs font-bold text-gray-600 uppercase tracking-wide mb-2 block">
                                          Remarks
                                        </span>
                                        <p className="text-sm text-gray-600 italic leading-relaxed">
                                          {actionData["Remarks"]}
                                        </p>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}

                        {testCase.expected && (
                          <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-teal-50 rounded-lg border-2 border-green-300 shadow-sm">
                            <p className="text-sm font-bold text-green-700 mb-2 flex items-center">
                              <CheckCircle className="h-4 w-4 mr-2" />
                              Overall Expected Result
                            </p>
                            <p className="text-gray-700 font-medium leading-relaxed">{testCase.expected}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TestCaseEditor;
