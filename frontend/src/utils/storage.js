// Local storage utilities for API key management

const STORAGE_KEYS = {
  OPENAI_API_KEY: "openai_api_key",
};

export const storage = {
  // Get API key from localStorage
  getApiKey: () => {
    try {
      return localStorage.getItem(STORAGE_KEYS.OPENAI_API_KEY);
    } catch (error) {
      console.error("Error reading API key from localStorage:", error);
      return null;
    }
  },

  // Set API key in localStorage
  setApiKey: (apiKey) => {
    try {
      if (apiKey) {
        localStorage.setItem(STORAGE_KEYS.OPENAI_API_KEY, apiKey);
      } else {
        localStorage.removeItem(STORAGE_KEYS.OPENAI_API_KEY);
      }
      return true;
    } catch (error) {
      console.error("Error saving API key to localStorage:", error);
      return false;
    }
  },

  // Remove API key from localStorage
  removeApiKey: () => {
    try {
      localStorage.removeItem(STORAGE_KEYS.OPENAI_API_KEY);
      return true;
    } catch (error) {
      console.error("Error removing API key from localStorage:", error);
      return false;
    }
  },

  // Check if API key exists
  hasApiKey: () => {
    const apiKey = storage.getApiKey();
    return apiKey && apiKey.length > 0;
  },

  // Validate API key format
  validateApiKey: (apiKey) => {
    if (!apiKey || typeof apiKey !== "string") {
      return false;
    }

    // OpenAI API keys start with 'sk-' and contain alphanumeric characters, underscores, and hyphens
    const openaiKeyPattern = /^sk-[a-zA-Z0-9_-]+$/;
    return openaiKeyPattern.test(apiKey);
  },

  // Get validated API key
  getValidatedApiKey: () => {
    const apiKey = storage.getApiKey();
    if (apiKey && storage.validateApiKey(apiKey)) {
      return apiKey;
    }
    return null;
  },
};

export default storage;
