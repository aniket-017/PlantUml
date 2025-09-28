import React, { createContext, useReducer } from "react";
import { ACTIONS } from "./actions";

// Initial state
const initialState = {
  currentStep: "landing", // 'landing', 'api-key', 'upload', 'edit', 'diagram', 'chat'
  apiKey: null,
  uploadedFile: null,
  testCases: [],
  plantUMLCode: "",
  plantUMLImage: "",
  chatHistory: [],
  loading: false,
  error: null,
};

// Reducer function
const appReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };

    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload, loading: false };

    case ACTIONS.CLEAR_ERROR:
      return { ...state, error: null };

    case ACTIONS.SET_STEP:
      return { ...state, currentStep: action.payload };

    case ACTIONS.SET_API_KEY:
      return { ...state, apiKey: action.payload };

    case ACTIONS.SET_UPLOADED_FILE:
      return { ...state, uploadedFile: action.payload };

    case ACTIONS.SET_TEST_CASES:
      return { ...state, testCases: action.payload };

    case ACTIONS.UPDATE_TEST_CASE: {
      const updatedTestCases = state.testCases.map((tc) =>
        tc.id === action.payload.id ? { ...tc, ...action.payload.updates } : tc
      );
      return { ...state, testCases: updatedTestCases };
    }

    case ACTIONS.SET_PLANTUML_DATA:
      return {
        ...state,
        plantUMLCode: action.payload.code,
        plantUMLImage: action.payload.image,
      };

    case ACTIONS.ADD_CHAT_MESSAGE:
      return {
        ...state,
        chatHistory: [...state.chatHistory, action.payload],
      };

    case ACTIONS.RESET_STATE:
      return initialState;

    default:
      return state;
  }
};

// Create context
export const AppContext = createContext();

// Provider component
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const value = {
    state,
    dispatch,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
