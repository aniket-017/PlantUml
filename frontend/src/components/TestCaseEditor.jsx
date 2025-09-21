import React, { useState } from 'react';
import { Edit2, ArrowLeft, ArrowRight, AlertCircle, FileText, User, CheckCircle } from 'lucide-react';
import { useApp } from '../hooks/useApp';
import { updateTestCase, setStep, setLoading, setError, setPlantUMLData } from '../context/actions';
import { apiService } from '../services/api';

const TestCaseEditor = () => {
  const { state, dispatch } = useApp();
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  // Parse JSON action data safely
  const parseActionData = (action) => {
    try {
      if (typeof action === 'string') {
        return JSON.parse(action);
      }
      return action;
    } catch {
      return { Steps: action || 'No steps provided' };
    }
  };

  const handleEdit = (testCase) => {
    setEditingId(testCase.id);
    setEditForm({
      title: testCase.title,
      expected: testCase.expected || '',
      description: testCase.description || ''
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

  const handleGenerateDiagram = async () => {
    try {
      setLoading(dispatch, true);
      const result = await apiService.generateDiagram(state.testCases);
      
      if (result.success) {
        setPlantUMLData(dispatch, result.plantuml_code, result.plantuml_image);
        setStep(dispatch, 'diagram');
      } else {
        setError(dispatch, 'Failed to generate diagram');
      }
    } catch (error) {
      setError(dispatch, error.message || 'Failed to generate diagram');
    } finally {
      setLoading(dispatch, false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Edit Test Cases</h1>
          <p className="text-gray-600 mt-1">
            Review and modify your test cases before generating the diagram
          </p>
        </div>
        <button
          onClick={() => setStep(dispatch, 'upload')}
          className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Upload
        </button>
      </div>

      {state.error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
          <AlertCircle className="h-5 w-5 mr-2" />
          {state.error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800">
              Test Cases ({state.testCases.length})
            </h2>
            <div className="space-x-3">
              <button
                onClick={handleGenerateDiagram}
                disabled={state.loading || state.testCases.length === 0}
                className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {state.loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <ArrowRight className="h-4 w-4 mr-2" />
                )}
                Generate Diagram
              </button>
            </div>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {state.testCases.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <p>No test cases found. Please upload a valid file.</p>
            </div>
          ) : (
            state.testCases.map((testCase) => (
              <div key={testCase.id} className="p-6">
                {editingId === testCase.id ? (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Title
                      </label>
                      <input
                        type="text"
                        value={editForm.title}
                        onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Test case title"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        value={editForm.description}
                        onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Test case description"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Expected Result
                      </label>
                      <textarea
                        value={editForm.expected}
                        onChange={(e) => setEditForm({ ...editForm, expected: e.target.value })}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Expected result"
                      />
                    </div>

                    <div className="flex space-x-3">
                      <button
                        onClick={handleSave}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                      >
                        Save
                      </button>
                      <button
                        onClick={handleCancel}
                        className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <FileText className="h-5 w-5 text-blue-600 mr-2" />
                          <h3 className="text-lg font-medium text-gray-800">
                            {testCase.title}
                          </h3>
                        </div>
                        <p className="text-sm text-gray-500">ID: {testCase.id}</p>
                      </div>
                      <button
                        onClick={() => handleEdit(testCase)}
                        className="flex items-center px-3 py-2 text-blue-600 hover:text-blue-800 bg-blue-50 rounded-md transition-colors"
                      >
                        <Edit2 className="h-4 w-4 mr-1" />
                        Edit
                      </button>
                    </div>

                    {testCase.description && (
                      <div className="mb-4">
                        <p className="text-sm font-medium text-gray-700 mb-1">Description:</p>
                        <p className="text-gray-600">{testCase.description}</p>
                      </div>
                    )}

                    {testCase.steps && testCase.steps.length > 0 && (
                      <div className="mb-4">
                        <p className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Test Case Details:
                        </p>
                        {testCase.steps.map((step, index) => {
                          const actionData = parseActionData(step.action);
                          return (
                            <div key={index} className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 p-4 rounded-lg mb-3">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {actionData['Test Case ID'] && (
                                  <div>
                                    <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">Test Case ID</span>
                                    <p className="text-sm text-gray-800 font-medium">{actionData['Test Case ID']}</p>
                                  </div>
                                )}
                                
                                {actionData['Scenario'] && (
                                  <div>
                                    <span className="text-xs font-semibold text-green-600 uppercase tracking-wide">Scenario</span>
                                    <p className="text-sm text-gray-800">{actionData['Scenario']}</p>
                                  </div>
                                )}

                                {actionData['Preconditions'] && (
                                  <div className="md:col-span-2">
                                    <span className="text-xs font-semibold text-orange-600 uppercase tracking-wide">Preconditions</span>
                                    <p className="text-sm text-gray-700">{actionData['Preconditions']}</p>
                                  </div>
                                )}

                                {actionData['Steps'] && (
                                  <div className="md:col-span-2">
                                    <span className="text-xs font-semibold text-purple-600 uppercase tracking-wide">Steps</span>
                                    <div className="text-sm text-gray-700 mt-1">
                                      {actionData['Steps'].split(/\d+\./).filter(step => step.trim()).map((stepText, stepIndex) => (
                                        <div key={stepIndex} className="flex items-start mb-1">
                                          <span className="text-purple-600 font-medium mr-2">{stepIndex + 1}.</span>
                                          <span>{stepText.trim()}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {actionData['Expected Result'] && (
                                  <div className="md:col-span-2">
                                    <span className="text-xs font-semibold text-green-600 uppercase tracking-wide">Expected Result</span>
                                    <p className="text-sm text-gray-700 bg-green-50 p-2 rounded border border-green-200">{actionData['Expected Result']}</p>
                                  </div>
                                )}

                                {actionData['Remarks'] && (
                                  <div className="md:col-span-2">
                                    <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Remarks</span>
                                    <p className="text-sm text-gray-600 italic">{actionData['Remarks']}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {testCase.expected && (
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-700">Overall Expected Result:</p>
                        <p className="text-gray-600 mt-1 bg-gray-50 p-2 rounded">{testCase.expected}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default TestCaseEditor;