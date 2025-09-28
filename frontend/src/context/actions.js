// Action types
export const ACTIONS = {
  SET_LOADING: "SET_LOADING",
  SET_ERROR: "SET_ERROR",
  CLEAR_ERROR: "CLEAR_ERROR",
  SET_STEP: "SET_STEP",
  SET_API_KEY: "SET_API_KEY",
  SET_UPLOADED_FILE: "SET_UPLOADED_FILE",
  SET_TEST_CASES: "SET_TEST_CASES",
  UPDATE_TEST_CASE: "UPDATE_TEST_CASE",
  SET_PLANTUML_DATA: "SET_PLANTUML_DATA",
  ADD_CHAT_MESSAGE: "ADD_CHAT_MESSAGE",
  RESET_STATE: "RESET_STATE",
};

// Action creators (helper functions)
export const setLoading = (dispatch, loading) => {
  dispatch({ type: ACTIONS.SET_LOADING, payload: loading });
};

export const setError = (dispatch, error) => {
  dispatch({ type: ACTIONS.SET_ERROR, payload: error });
};

export const clearError = (dispatch) => {
  dispatch({ type: ACTIONS.CLEAR_ERROR });
};

export const setStep = (dispatch, step) => {
  dispatch({ type: ACTIONS.SET_STEP, payload: step });
};

export const setApiKey = (dispatch, apiKey) => {
  dispatch({ type: ACTIONS.SET_API_KEY, payload: apiKey });
};

export const setUploadedFile = (dispatch, file) => {
  dispatch({ type: ACTIONS.SET_UPLOADED_FILE, payload: file });
};

export const setTestCases = (dispatch, testCases) => {
  dispatch({ type: ACTIONS.SET_TEST_CASES, payload: testCases });
};

export const updateTestCase = (dispatch, id, updates) => {
  dispatch({ type: ACTIONS.UPDATE_TEST_CASE, payload: { id, updates } });
};

export const setPlantUMLData = (dispatch, code, image) => {
  dispatch({ type: ACTIONS.SET_PLANTUML_DATA, payload: { code, image } });
};

export const addChatMessage = (dispatch, message) => {
  dispatch({ type: ACTIONS.ADD_CHAT_MESSAGE, payload: message });
};

export const resetState = (dispatch) => {
  dispatch({ type: ACTIONS.RESET_STATE });
};
