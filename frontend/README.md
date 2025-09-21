# CSV to PlantUML Generator - Frontend

A modern React frontend for converting CSV/Excel files to PlantUML diagrams with AI-powered refinement capabilities.

## Features

- 📁 **File Upload**: Drag & drop or click to upload CSV/Excel files
- ✏️ **Test Case Editor**: Review and modify test cases before diagram generation
- 🎨 **Diagram Viewer**: View generated PlantUML diagrams with download capabilities
- 🤖 **AI Chat Interface**: Refine diagrams using natural language prompts
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🎯 **Progress Tracking**: Visual step indicator for the entire workflow

## Technology Stack

- **React 19**: Modern React with latest features
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Lucide React**: Beautiful icon library
- **Axios**: HTTP client for API communication
- **Vite**: Fast build tool and dev server

## Prerequisites

- Node.js 18+ and npm
- The PlantUML backend server running on `http://127.0.0.1:8000`

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Install additional required packages:**
   ```bash
   npm install react-router-dom axios lucide-react
   ```

## Development

1. **Start the development server:**
   ```bash
   npm run dev
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5173
   ```

## Building for Production

1. **Build the project:**
   ```bash
   npm run build
   ```

2. **Preview the production build:**
   ```bash
   npm run preview
   ```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── FileUpload.jsx   # File upload with drag & drop
│   │   ├── TestCaseEditor.jsx # Test case editing interface
│   │   ├── DiagramViewer.jsx  # Diagram display and actions
│   │   ├── ChatInterface.jsx  # AI chat for diagram refinement
│   │   ├── StepIndicator.jsx  # Progress indicator
│   │   ├── LoadingSpinner.jsx # Loading states
│   │   ├── Toast.jsx         # Notification toasts
│   │   └── ErrorBoundary.jsx # Error handling
│   ├── context/             # React Context for state management
│   │   ├── AppContext.jsx   # Main application context
│   │   └── actions.js       # Action creators and constants
│   ├── hooks/               # Custom React hooks
│   │   └── useApp.js        # Hook for accessing app context
│   ├── services/            # API service layer
│   │   └── api.js          # Backend API communication
│   ├── App.jsx             # Main application component
│   ├── main.jsx            # Application entry point
│   ├── index.css           # Global styles with Tailwind
│   └── App.css             # Component-specific styles
├── public/                 # Static assets
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── vite.config.js         # Vite configuration
```

## Application Flow

1. **Upload**: Users upload CSV or Excel files
2. **Edit**: Review and modify extracted test cases
3. **Generate**: Create PlantUML diagrams from test cases
4. **Refine**: Use AI chat to improve and customize diagrams

## Configuration

### API Endpoint
The frontend expects the backend to be running on `http://127.0.0.1:8000`. To change this, update the `BASE_URL` in `src/services/api.js`.

### Styling
The application uses Tailwind CSS for styling. Customize the theme in `tailwind.config.js`.

## API Integration

The frontend communicates with the backend using these endpoints:

- `POST /upload-csv/` - Upload and parse CSV/Excel files
- `POST /generate-diagram/` - Generate PlantUML diagrams
- `POST /chat-plantuml/` - Refine diagrams with AI chat
- `GET /static/*` - Serve generated diagram images

## Error Handling

- Network errors are displayed with retry options
- File validation prevents invalid uploads
- Loading states provide user feedback
- Error boundaries catch and display React errors

## Performance Features

- Lazy loading for better initial load times
- Optimized images and assets
- Efficient state management with React Context
- Tailwind CSS for optimal CSS bundle size

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+

## Troubleshooting

1. **Port conflicts**: If port 5173 is busy, Vite will automatically use the next available port
2. **Backend connectivity**: Ensure the FastAPI server is running and accessible
3. **CORS issues**: The backend should have CORS configured for the frontend domain

## Development Tips

- Use browser dev tools to inspect network requests
- Check the console for error messages
- Use React DevTools extension for debugging
- Test file uploads with various CSV/Excel formats

## Contributing

1. Follow the existing code style and patterns
2. Add proper error handling for new features
3. Include loading states for async operations
4. Test responsive design on different screen sizes
5. Update this README when adding new features+ Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
