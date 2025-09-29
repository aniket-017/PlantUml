import React from "react";
import { ArrowRight, FileText, Brain, Image, MessageCircle, Upload, Key } from "lucide-react";
import { useApp } from "../hooks/useApp";
import { setStep } from "../context/actions";

const LandingPage = () => {
  const { dispatch } = useApp();

  const handleGetStarted = () => {
    setStep(dispatch, "api-key");
  };

  const features = [
    {
      icon: Upload,
      title: "Upload Files",
      description: "Upload CSV or Excel files with your test cases",
    },
    {
      icon: FileText,
      title: "Edit Test Cases",
      description: "Review and modify test cases before processing",
    },
    {
      icon: Brain,
      title: "AI Processing",
      description: "Generate PlantUML diagrams using OpenAI's intelligence",
    },
    {
      icon: Image,
      title: "Visual Diagrams",
      description: "View beautiful, professional PlantUML diagrams",
    },
    {
      icon: MessageCircle,
      title: "AI Refinement",
      description: "Chat with AI to improve and refine your diagrams",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Transform Your
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                {" "}
                Test Cases
              </span>
              <br />
              into Visual Diagrams
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              Upload your CSV or Excel test cases and let our AI-powered platform generate beautiful PlantUML diagrams
              automatically. Refine and perfect your visualizations through intelligent chat assistance.
            </p>
            <button
              onClick={handleGetStarted}
              className="inline-flex items-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              A simple 5-step process to transform your test cases into professional diagrams
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="group p-6 bg-white rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all duration-300"
                >
                  <div className="flex items-center mb-4">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-4">
                      <span className="text-sm font-semibold text-blue-600">Step {index + 1}</span>
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Ready to Visualize Your Test Cases?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of developers who are already creating better documentation with AI-powered diagram
            generation.
          </p>
          <button
            onClick={handleGetStarted}
            className="inline-flex items-center px-8 py-4 text-lg font-semibold text-blue-600 bg-white rounded-xl hover:bg-gray-50 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            Start Creating Diagrams
            <ArrowRight className="ml-2 h-5 w-5" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-4">Test Case Generator</h3>
            
            <div className="flex justify-center space-x-6">
              <div className="flex items-center text-gray-400">
                <Key className="h-5 w-5 mr-2" />
                <span>Secure API Integration</span>
              </div>
              <div className="flex items-center text-gray-400">
                <Brain className="h-5 w-5 mr-2" />
                <span>AI-Powered</span>
              </div>
              <div className="flex items-center text-gray-400">
                <Image className="h-5 w-5 mr-2" />
                <span>Professional Diagrams</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;



