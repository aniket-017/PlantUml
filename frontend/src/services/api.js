const BASE_URL = 'http://localhost:2004';

class ApiService {
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${BASE_URL}/upload-csv/`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async generateDiagram(testCases) {
    const response = await fetch(`${BASE_URL}/generate-diagram/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        test_cases: testCases
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async chatWithPlantUML(plantUMLCode, message) {
    const response = await fetch(`${BASE_URL}/chat-plantuml/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        plantuml_code: plantUMLCode,
        message: message
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
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