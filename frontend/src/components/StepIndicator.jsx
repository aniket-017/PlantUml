import React from 'react';
import { Upload, Edit, Image, MessageCircle, Check } from 'lucide-react';
import { useApp } from '../hooks/useApp';

const StepIndicator = () => {
  const { state } = useApp();

  const steps = [
    {
      id: 'upload',
      title: 'Upload File',
      icon: Upload,
      description: 'Upload CSV or Excel file'
    },
    {
      id: 'edit',
      title: 'Edit Test Cases',
      icon: Edit,
      description: 'Review and modify test cases'
    },
    {
      id: 'diagram',
      title: 'View Diagram',
      icon: Image,
      description: 'Generated PlantUML diagram'
    },
    {
      id: 'chat',
      title: 'Refine with AI',
      icon: MessageCircle,
      description: 'Chat to improve diagram'
    }
  ];

  const getStepStatus = (stepId) => {
    const currentIndex = steps.findIndex(step => step.id === state.currentStep);
    const stepIndex = steps.findIndex(step => step.id === stepId);
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'current';
    return 'upcoming';
  };

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6 py-4">
        <nav aria-label="Progress">
          <ol className="flex items-center justify-between">
            {steps.map((step, stepIdx) => {
              const status = getStepStatus(step.id);
              const Icon = step.icon;
              
              return (
                <li key={step.id} className="relative flex-1">
                  <div className={`flex items-center ${stepIdx !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''}`}>
                    <div className="relative flex items-center justify-center">
                      <div
                        className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
                          status === 'completed'
                            ? 'bg-blue-600 border-blue-600'
                            : status === 'current'
                            ? 'border-blue-600 bg-white'
                            : 'border-gray-300 bg-white'
                        }`}
                      >
                        {status === 'completed' ? (
                          <Check className="h-5 w-5 text-white" />
                        ) : (
                          <Icon
                            className={`h-5 w-5 ${
                              status === 'current' ? 'text-blue-600' : 'text-gray-400'
                            }`}
                          />
                        )}
                      </div>
                    </div>
                    
                    <div className="ml-4 min-w-0 flex-1">
                      <div
                        className={`text-sm font-medium ${
                          status === 'current' ? 'text-blue-600' : 
                          status === 'completed' ? 'text-gray-900' : 'text-gray-500'
                        }`}
                      >
                        {step.title}
                      </div>
                      <div className="text-xs text-gray-500">{step.description}</div>
                    </div>
                  </div>

                  {/* Connector */}
                  {stepIdx !== steps.length - 1 && (
                    <div
                      className="absolute top-5 right-0 hidden h-0.5 w-8 sm:w-20 sm:block"
                      style={{
                        backgroundColor: getStepStatus(steps[stepIdx + 1].id) !== 'upcoming' ? '#2563eb' : '#d1d5db'
                      }}
                    />
                  )}
                </li>
              );
            })}
          </ol>
        </nav>
      </div>
    </div>
  );
};

export default StepIndicator;