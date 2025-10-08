import React, { useState, useRef, useEffect } from "react";
import { Send, ArrowLeft, Bot, User, AlertCircle } from "lucide-react";
import { useApp } from "../hooks/useApp";
import { setStep, setLoading, setError, setPlantUMLData, addChatMessage } from "../context/actions";
import { apiService } from "../services/api";

const ChatInterface = () => {
  const { state, dispatch } = useApp();
  const [message, setMessage] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.chatHistory]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || state.loading) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: message,
      timestamp: new Date(),
    };

    addChatMessage(dispatch, userMessage);
    setMessage("");

    try {
      setLoading(dispatch, true);
      const result =
        state.fileType === "cmdb"
          ? await apiService.chatWithCmdbPlantUML(state.plantUMLCode, message)
          : await apiService.chatWithPlantUML(state.plantUMLCode, message);

      if (result.success) {
        const botMessage = {
          id: Date.now() + 1,
          type: "bot",
          content: "I've updated your diagram based on your request.",
          timestamp: new Date(),
        };

        addChatMessage(dispatch, botMessage);
        setPlantUMLData(dispatch, result.plantuml_code, result.plantuml_image);
      } else {
        setError(dispatch, "Failed to process your request");
      }
    } catch (error) {
      setError(dispatch, error.message || "Failed to send message");
    } finally {
      setLoading(dispatch, false);
    }
  };

  const suggestedPrompts = [
    "Add a database actor and show it saving user data",
    "Include error handling flows",
    "Add more detailed user interactions",
    "Show system components and their relationships",
    "Add authentication flow",
  ];

  const handleSuggestedPrompt = (prompt) => {
    setMessage(prompt);
  };

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">Refine Your Diagram</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">
            Chat with AI to modify and improve your PlantUML diagram
          </p>
        </div>
        <button
          onClick={() => setStep(dispatch, "diagram")}
          className="flex items-center justify-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Diagram
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chat Interface */}
        <div className="order-2 lg:order-1">
          <div className="bg-white rounded-lg shadow-md h-[500px] sm:h-[600px] flex flex-col">
            <div className="p-3 sm:p-4 border-b border-gray-200">
              <h2 className="text-base sm:text-lg font-semibold text-gray-800">AI Assistant</h2>
              <p className="text-xs sm:text-sm text-gray-600">Ask me to modify your diagram</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
              {state.chatHistory.length === 0 ? (
                <div className="text-center text-gray-500 py-6 sm:py-8">
                  <Bot className="h-10 w-10 sm:h-12 sm:w-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-sm sm:text-base">Start a conversation to refine your diagram!</p>
                  <p className="text-xs sm:text-sm mt-2">
                    Try asking me to add actors, modify flows, or improve the structure.
                  </p>
                </div>
              ) : (
                state.chatHistory.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`max-w-[85%] sm:max-w-[80%] p-2 sm:p-3 rounded-lg ${
                        msg.type === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {msg.type === "bot" && <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />}
                        {msg.type === "user" && <User className="h-4 w-4 mt-0.5 flex-shrink-0" />}
                        <div className="flex-1">
                          <p className="text-xs sm:text-sm">{msg.content}</p>
                          <p className={`text-xs mt-1 ${msg.type === "user" ? "text-blue-200" : "text-gray-500"}`}>
                            {msg.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
              {state.loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-800 p-3 rounded-lg max-w-[80%]">
                    <div className="flex items-center space-x-2">
                      <Bot className="h-4 w-4" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Error Display */}
            {state.error && (
              <div className="p-4 bg-red-50 border-t border-red-200">
                <div className="flex items-center text-red-700">
                  <AlertCircle className="h-4 w-4 mr-2" />
                  <span className="text-sm">{state.error}</span>
                </div>
              </div>
            )}

            {/* Input Form */}
            <form onSubmit={handleSendMessage} className="p-3 sm:p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type your message..."
                  disabled={state.loading}
                  className="flex-1 px-2 sm:px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 text-sm sm:text-base"
                />
                <button
                  type="submit"
                  disabled={!message.trim() || state.loading}
                  className="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </form>
          </div>

          {/* Suggested Prompts */}
          {state.chatHistory.length === 0 && (
            <div className="mt-4 bg-blue-50 rounded-lg p-3 sm:p-4">
              <h3 className="text-xs sm:text-sm font-semibold text-blue-800 mb-2">Suggested prompts:</h3>
              <div className="space-y-1 sm:space-y-2">
                {suggestedPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestedPrompt(prompt)}
                    className="block w-full text-left text-xs sm:text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 p-2 rounded transition-colors"
                  >
                    "{prompt}"
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Live Diagram Preview */}
        <div className="order-1 lg:order-2">
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-3 sm:p-4 border-b border-gray-200">
              <h2 className="text-base sm:text-lg font-semibold text-gray-800">Live Preview</h2>
              <p className="text-xs sm:text-sm text-gray-600">Updates automatically as you chat</p>
            </div>

            <div className="p-4 sm:p-6">
              {state.plantUMLImage ? (
                <div className="text-center">
                  <img
                    key={`diagram-${Date.now()}-${state.plantUMLImage}`}
                    src={`${apiService.getImageUrl(state.plantUMLImage)}?t=${Date.now()}`}
                    alt="Updated PlantUML Diagram"
                    className="max-w-full h-auto mx-auto border border-gray-200 rounded-lg shadow-sm"
                    onError={(e) => {
                      e.target.style.display = "none";
                      e.target.nextSibling.style.display = "block";
                    }}
                  />
                  <div style={{ display: "none" }} className="text-red-500 p-4">
                    Failed to load diagram image
                  </div>
                  <div className="mt-2 text-xs text-gray-500">Last updated: {new Date().toLocaleTimeString()}</div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <p>No diagram available</p>
                </div>
              )}
            </div>
          </div>

          <div className="mt-4 bg-gray-50 rounded-lg p-3 sm:p-4">
            <h4 className="font-semibold text-gray-800 mb-2 text-sm sm:text-base">💡 Chat Tips</h4>
            <div className="space-y-1 text-xs sm:text-sm text-gray-600">
              <p>• Be specific about what you want to add or change</p>
              <p>• Ask for actors, relationships, or flow modifications</p>
              <p>• Request error handling or alternative scenarios</p>
              <p>• The diagram will update automatically after each response</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
