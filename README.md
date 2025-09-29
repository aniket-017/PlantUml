# PlantUML Test Case Generator

A full-stack application that converts CSV/Excel test case data into comprehensive PlantUML sequence diagrams with AI-powered enhancement capabilities.

## 🚀 Features

- **CSV/Excel Upload**: Upload test case data in CSV or Excel format
- **AI-Powered Enhancement**: Uses OpenAI to analyze data and generate comprehensive test coverage
- **Interactive Editor**: Edit and refine test cases before diagram generation
- **PlantUML Generation**: Automatically creates sequence diagrams from test cases
- **Real-time Chat**: Chat with AI to refine and improve PlantUML diagrams
- **Modern UI**: Built with React and Tailwind CSS for a smooth user experience

## 🏗️ Architecture

The project consists of two main components:

### Backend (FastAPI + Python)

- **Location**: `plantuml2/`
- **Framework**: FastAPI
- **Key Services**:
  - CSV processing and test case construction
  - AI-powered test case enhancement
  - PlantUML diagram generation
  - File upload and management

### Frontend (React + Vite)

- **Location**: `frontend/`
- **Framework**: React 19 with Vite
- **Styling**: Tailwind CSS
- **Key Components**:
  - File upload interface
  - Test case editor
  - Diagram viewer
  - Chat interface for AI interaction

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Java** (for PlantUML rendering)
- **OpenAI API Key** (for AI enhancement features)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd PlantUml
```

### 2. Backend Setup

```bash
cd plantuml2
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Build Frontend

```bash
npm run build
```

## 🚀 Running the Application

### Option 1: Using the Batch Script (Windows)

```bash
cd plantuml2
start_server.bat
```

### Option 2: Manual Start

```bash
# Terminal 1 - Backend
cd plantuml2
python run_server.py

# Terminal 2 - Frontend (if running in dev mode)
cd frontend
npm run dev
```

The application will be available at `http://localhost:8000`

## 📖 Usage

### 1. **API Key Setup**

- Enter your OpenAI API key to enable AI-powered features
- The API key is used for test case enhancement and diagram refinement

### 2. **File Upload**

- Upload CSV or Excel files containing test case data
- Supported formats: `.csv`, `.xlsx`, `.xls`
- The system will automatically convert Excel files to CSV

### 3. **Test Case Enhancement**

- AI analyzes your data to identify missing test scenarios
- Generates comprehensive test coverage including:
  - Happy path testing
  - Error handling scenarios
  - Edge cases and boundary conditions
  - Integration testing
  - Data validation scenarios

### 4. **Edit Test Cases**

- Review and modify generated test cases
- Add, edit, or remove test steps
- Customize actors and actions

### 5. **Generate Diagrams**

- Convert test cases to PlantUML sequence diagrams
- View generated diagrams in the browser
- Download diagrams as PNG files

### 6. **AI Chat Interface**

- Chat with AI to refine and improve diagrams
- Ask for specific modifications or improvements
- Get suggestions for better test coverage

## 🔧 API Endpoints

### Backend API

- `GET /` - Serve frontend application
- `GET /health` - Health check
- `GET /test-case-info` - Get information about test case capabilities
- `POST /upload-csv/` - Upload and process CSV/Excel files
- `POST /generate-diagram/` - Generate PlantUML diagrams from test cases
- `POST /chat-plantuml/` - Chat with AI to refine diagrams

### Static Files

- `/static/` - Generated PlantUML diagrams and images
- `/assets/` - Frontend static assets

## 📁 Project Structure

```
PlantUml/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── context/         # State management
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   └── utils/           # Utility functions
│   ├── dist/                # Built frontend
│   └── package.json
├── plantuml2/               # FastAPI backend
│   ├── app/
│   │   ├── services/        # Core services
│   │   └── main.py          # FastAPI application
│   ├── uploads/             # Uploaded files
│   ├── static/              # Generated diagrams
│   └── requirements.txt
└── README.md
```

## 🎯 Key Features Explained

### AI-Powered Test Case Enhancement

- **Pattern Detection**: Automatically identifies data patterns and relationships
- **Coverage Expansion**: Generates additional test cases for complete coverage
- **Edge Case Generation**: Includes boundary conditions and error scenarios
- **Actor Identification**: Identifies all possible actors and user roles

### PlantUML Integration

- **Local Rendering**: Uses local PlantUML JAR for diagram generation
- **Multiple Formats**: Supports various PlantUML diagram types
- **Error Handling**: Comprehensive error handling for PlantUML syntax issues

### Modern UI/UX

- **Step-by-Step Process**: Clear workflow with step indicators
- **Real-time Feedback**: Loading states and progress indicators
- **Responsive Design**: Works on desktop and mobile devices
- **Error Boundaries**: Graceful error handling and recovery

## 🔒 Security Notes

- API keys are handled securely and not stored permanently
- File uploads are validated and sanitized
- CORS is configured for development (should be restricted in production)

## 🐛 Troubleshooting

### Common Issues

1. **PlantUML JAR not found**

   - Ensure `plantuml.jar` is in the `plantuml2/app/` directory
   - Download from [PlantUML website](https://plantuml.com/download)

2. **Java not found**

   - Install Java Runtime Environment (JRE) 8 or higher
   - Ensure Java is in your system PATH

3. **OpenAI API errors**

   - Verify your API key is correct and has sufficient credits
   - Check API key permissions

4. **Frontend not loading**
   - Ensure frontend is built: `npm run build`
   - Check that `frontend/dist/` directory exists

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [PlantUML](https://plantuml.com/) for diagram generation
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
- [OpenAI](https://openai.com/) for AI capabilities
- [Tailwind CSS](https://tailwindcss.com/) for styling
