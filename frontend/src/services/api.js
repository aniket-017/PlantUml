const BASE_URL = "https://poc1.prashantpukale.com";
// const BASE_URL = "http://localhost:2004";

class ApiService {
  constructor() {
    this.apiKey = null;
  }

  setApiKey(apiKey) {
    this.apiKey = apiKey;
  }

  getHeaders(includeContentType = true) {
    const headers = {};

    if (includeContentType) {
      headers["Content-Type"] = "application/json";
    }

    if (this.apiKey) {
      headers["X-OpenAI-API-Key"] = this.apiKey;
    }

    return headers;
  }
  async uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/upload-csv/`, {
      method: "POST",
      headers: this.getHeaders(false), // Don't include Content-Type for FormData
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async generateDiagram(testCases) {
    if (!this.apiKey) {
      throw new Error("OpenAI API key is required. Please set your API key first.");
    }

    const response = await fetch(`${BASE_URL}/generate-diagram/`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        test_cases: testCases,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async chatWithPlantUML(plantUMLCode, message) {
    if (!this.apiKey) {
      throw new Error("OpenAI API key is required. Please set your API key first.");
    }

    const response = await fetch(`${BASE_URL}/chat-plantuml/`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        plantuml_code: plantUMLCode,
        message: message,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async healthCheck() {
    const response = await fetch(`${BASE_URL}/health`);
    return await response.json();
  }

  getImageUrl(imagePath) {
    return `${BASE_URL}${imagePath}`;
  }
}

export const apiService = new ApiService();
