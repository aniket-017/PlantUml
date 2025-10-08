import React, { useState } from "react";
import { Database, Plus, Trash2, Edit3, Save, X, ArrowRight, Server, Network, HardDrive } from "lucide-react";
import { useApp } from "../hooks/useApp";
import { updateCmdbItem, setLoading, setError, setStep, setPlantUMLData } from "../context/actions";
import { apiService } from "../services/api";

const CmdbEditor = () => {
  const { state, dispatch } = useApp();
  const [editingItem, setEditingItem] = useState(null);
  const [newItem, setNewItem] = useState({
    name: "",
    type: "",
    description: "",
    attributes: {},
    relationships: [],
  });

  const handleEdit = (item) => {
    setEditingItem(item.id);
  };

  const handleSave = (itemId, updates) => {
    updateCmdbItem(dispatch, itemId, updates);
    setEditingItem(null);
  };

  const handleCancel = () => {
    setEditingItem(null);
  };

  const handleAddItem = () => {
    if (newItem.name && newItem.type) {
      const item = {
        id: Date.now().toString(),
        ...newItem,
        attributes: Object.keys(newItem.attributes).length > 0 ? newItem.attributes : {},
        relationships: newItem.relationships || [],
      };

      // Add to state (this would need a new action in a real implementation)
      console.log("Adding new item:", item);
      setNewItem({
        name: "",
        type: "",
        description: "",
        attributes: {},
        relationships: [],
      });
    }
  };

  const handleGenerateDiagram = async () => {
    try {
      setLoading(dispatch, true);
      const result = await apiService.generateCmdbDiagram(state.cmdbItems);

      if (result.success) {
        // Set the PlantUML data in the state so DiagramViewer can display it
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

  const getItemIcon = (type) => {
    switch (type.toLowerCase()) {
      case "server":
      case "host":
        return <Server className="h-4 w-4" />;
      case "network":
      case "switch":
      case "router":
        return <Network className="h-4 w-4" />;
      case "storage":
      case "database":
        return <HardDrive className="h-4 w-4" />;
      default:
        return <Database className="h-4 w-4" />;
    }
  };

  const CmdbItemCard = ({ item }) => {
    const isEditing = editingItem === item.id;

    if (isEditing) {
      return (
        <div className="bg-white border-2 border-blue-300 rounded-lg p-4 shadow-lg">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  defaultValue={item.name}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    // Handle name update
                  }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <input
                  type="text"
                  defaultValue={item.type}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    // Handle type update
                  }}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                defaultValue={item.description}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                onChange={(e) => {
                  // Handle description update
                }}
              />
            </div>

            <div className="flex justify-end space-x-2">
              <button
                onClick={() => handleSave(item.id, {})}
                className="inline-flex items-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                <Save className="h-4 w-4 mr-1" />
                Save
              </button>
              <button
                onClick={handleCancel}
                className="inline-flex items-center px-3 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
              >
                <X className="h-4 w-4 mr-1" />
                Cancel
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              {getItemIcon(item.type)}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{item.name}</h3>
              <p className="text-sm text-blue-600 font-medium">{item.type}</p>
              {item.description && <p className="text-sm text-gray-600 mt-1">{item.description}</p>}
            </div>
          </div>
          <button
            onClick={() => handleEdit(item)}
            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
          >
            <Edit3 className="h-4 w-4" />
          </button>
        </div>

        {item.attributes && Object.keys(item.attributes).length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Attributes:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {Object.entries(item.attributes).map(([key, value]) => (
                <div key={key} className="text-sm">
                  <span className="font-medium text-gray-600">{key}:</span>
                  <span className="ml-1 text-gray-500">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {item.relationships && item.relationships.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Relationships:</h4>
            <div className="space-y-1">
              {item.relationships.map((rel, index) => (
                <div key={index} className="text-sm text-gray-600">
                  <span className="font-medium">{rel.type}:</span>
                  <span className="ml-1">{rel.target}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6">
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center mr-4">
            <Database className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">CMDB Items Editor</h1>
            <p className="text-gray-600">Review and edit your CMDB items before generating the architecture diagram</p>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <Database className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-800">Found {state.cmdbItems.length} CMDB items</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="space-y-4">
            {state.cmdbItems.map((item) => (
              <CmdbItemCard key={item.id} item={item} />
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Add New Item</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newItem.name}
                  onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Web Server 01"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <input
                  type="text"
                  value={newItem.type}
                  onChange={(e) => setNewItem({ ...newItem, type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Server, Database, Application"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newItem.description}
                  onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of the component"
                />
              </div>
              <button
                onClick={handleAddItem}
                className="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Item
              </button>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Ready to Generate?</h3>
            <p className="text-sm text-gray-600 mb-4">
              Once you're satisfied with your CMDB items, generate the system architecture diagram.
            </p>
            <button
              onClick={handleGenerateDiagram}
              disabled={state.loading}
              className="w-full inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {state.loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </>
              ) : (
                <>
                  Generate Architecture Diagram
                  <ArrowRight className="ml-2 h-5 w-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CmdbEditor;
