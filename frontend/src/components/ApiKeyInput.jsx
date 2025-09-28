import React, { useState, useEffect } from "react";
import { Key, Eye, EyeOff, CheckCircle, AlertCircle } from "lucide-react";

const ApiKeyInput = ({ onApiKeySet, initialValue = "" }) => {
  const [apiKey, setApiKey] = useState(initialValue);
  const [showKey, setShowKey] = useState(false);
  const [isValid, setIsValid] = useState(null);
  const [isChecking, setIsChecking] = useState(false);

  // Load API key from localStorage on component mount
  useEffect(() => {
    const savedApiKey = localStorage.getItem("openai_api_key");
    if (savedApiKey) {
      setApiKey(savedApiKey);
      setIsValid(true);
    }
  }, []);

  // Validate API key format
  const validateApiKey = (key) => {
    // OpenAI API keys start with 'sk-' and contain alphanumeric characters, underscores, and hyphens
    const openaiKeyPattern = /^sk-[a-zA-Z0-9_-]+$/;
    return openaiKeyPattern.test(key);
  };

  const handleApiKeyChange = (e) => {
    const value = e.target.value;
    setApiKey(value);

    if (value.length === 0) {
      setIsValid(null);
    } else {
      setIsValid(validateApiKey(value));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isValid) {
      return;
    }

    setIsChecking(true);

    try {
      // Save to localStorage
      localStorage.setItem("openai_api_key", apiKey);

      // Notify parent component
      onApiKeySet(apiKey);
    } catch (error) {
      console.error("Error saving API key:", error);
      // You could add error state handling here if needed
    } finally {
      setIsChecking(false);
    }
  };

  const handleClearKey = () => {
    setApiKey("");
    setIsValid(null);
    localStorage.removeItem("openai_api_key");
  };

  return (
    <div className="max-w-md mx-auto px-4 sm:px-0">
      <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
        <div className="text-center mb-6">
          <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <Key className="h-6 w-6 text-blue-600" />
          </div>
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">OpenAI API Key Required</h2>
          <p className="text-sm text-gray-600">Enter your OpenAI API key to generate PlantUML diagrams</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 mb-2">
              OpenAI API Key
            </label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                id="api-key"
                value={apiKey}
                onChange={handleApiKeyChange}
                placeholder="sk-..."
                className={`w-full px-3 py-2 pr-20 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  isValid === true
                    ? "border-green-300 bg-green-50"
                    : isValid === false
                    ? "border-red-300 bg-red-50"
                    : "border-gray-300"
                }`}
                disabled={isChecking}
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-12 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                disabled={isChecking}
              >
                {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
              {isValid === true && (
                <CheckCircle className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-green-500" />
              )}
              {isValid === false && (
                <AlertCircle className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-red-500" />
              )}
            </div>

            {isValid === false && (
              <p className="mt-1 text-sm text-red-600">Please enter a valid OpenAI API key (starts with 'sk-')</p>
            )}

            {isValid === true && <p className="mt-1 text-sm text-green-600">✓ Valid API key format</p>}
          </div>

          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
            <button
              type="submit"
              disabled={!isValid || isChecking}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isChecking ? "Saving..." : "Save & Continue"}
            </button>

            {apiKey && (
              <button
                type="button"
                onClick={handleClearKey}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                disabled={isChecking}
              >
                Clear
              </button>
            )}
          </div>
        </form>

        <div className="mt-6 p-4 bg-blue-50 rounded-md">
          <h3 className="text-sm font-medium text-blue-900 mb-2">How to get your API key:</h3>
          <ol className="text-sm text-blue-800 space-y-1">
            <li>
              1. Visit{" "}
              <a
                href="https://platform.openai.com/api-keys"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-blue-900"
              >
                OpenAI Platform
              </a>
            </li>
            <li>2. Sign in to your account</li>
            <li>3. Click "Create new secret key"</li>
            <li>4. Copy the key and paste it here</li>
          </ol>
        </div>

        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-xs text-yellow-800">
            <strong>Privacy Note:</strong> Your API key is stored locally in your browser and never sent to our servers
            except for processing your requests.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ApiKeyInput;
