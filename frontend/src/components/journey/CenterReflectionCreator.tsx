import React, { useState } from 'react';
import { useCenterData } from '../../hooks/journey/useCenterData';
import { CenterDataSelector } from './CenterDataSelector';

interface SelectedItem {
  id: string;
  data: any;
  type: string;
}

interface ReflectionPrompt {
  id: string;
  title: string;
  description: string;
  prompt: string;
}

const DEFAULT_PROMPTS: ReflectionPrompt[] = [
  {
    id: 'progress',
    title: 'Progress Reflection',
    description: 'Reflect on your progress and growth',
    prompt: 'Looking at your selected data, what progress have you made? What patterns do you notice?'
  },
  {
    id: 'challenges',
    title: 'Challenge Analysis',
    description: 'Explore obstacles and learning opportunities',
    prompt: 'What challenges have you encountered? How have they contributed to your growth?'
  },
  {
    id: 'insights',
    title: 'Key Insights',
    description: 'Discover meaningful insights and connections',
    prompt: 'What key insights emerge from this data? What connections do you see?'
  },
  {
    id: 'future',
    title: 'Future Planning',
    description: 'Plan your next steps and goals',
    prompt: 'Based on this reflection, what would you like to focus on moving forward?'
  }
];

export const CenterReflectionCreator: React.FC = () => {
  const { centerData, loading, error, refetch } = useCenterData();
  const [selectedItems, setSelectedItems] = useState<SelectedItem[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<ReflectionPrompt | null>(null);
  const [step, setStep] = useState<'select-data' | 'select-prompt' | 'create-reflection'>('select-data');

  const handleDataSelect = (id: string, data: any, type: string) => {
    setSelectedItems(prev => {
      const existingIndex = prev.findIndex(item => item.id === id);
      if (existingIndex >= 0) {
        // Remove if already selected
        return prev.filter(item => item.id !== id);
      } else {
        // Add new selection
        return [...prev, { id, data, type }];
      }
    });
  };

  const handlePromptSelect = (prompt: ReflectionPrompt) => {
    setSelectedPrompt(prompt);
  };

  const handleNextStep = () => {
    if (step === 'select-data' && selectedItems.length > 0) {
      setStep('select-prompt');
    } else if (step === 'select-prompt' && selectedPrompt) {
      setStep('create-reflection');
    }
  };

  const handlePreviousStep = () => {
    if (step === 'select-prompt') {
      setStep('select-data');
    } else if (step === 'create-reflection') {
      setStep('select-prompt');
    }
  };

  const handleStartReflection = () => {
    // This would typically navigate to a reflection creation interface
    // or trigger a modal/form for creating the reflection
    console.log('Starting reflection with:', {
      selectedItems,
      selectedPrompt
    });
    // TODO: Implement reflection creation logic
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-neutral-600">Loading your center data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="mb-4">
          <svg className="w-12 h-12 mx-auto text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-neutral-900 mb-2">Unable to load center data</h3>
        <p className="text-neutral-600 mb-4">{error}</p>
        <button
          onClick={refetch}
          className="btn-primary"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!centerData) {
    return (
      <div className="text-center py-12">
        <p className="text-neutral-600">No center data available.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-neutral-900 mb-2">
          Create Center Reflection
        </h1>
        <p className="text-neutral-600">
          Reflect on your goals, values, and growth patterns to gain deeper insights.
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center space-x-4">
          <div className={`flex items-center ${step === 'select-data' ? 'text-primary-600' : selectedItems.length > 0 ? 'text-success-600' : 'text-neutral-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step === 'select-data' ? 'bg-primary-100 text-primary-600' : 
              selectedItems.length > 0 ? 'bg-success-100 text-success-600' : 
              'bg-neutral-100 text-neutral-400'
            }`}>
              1
            </div>
            <span className="ml-2 font-medium">Select Data</span>
          </div>
          <div className={`w-8 h-0.5 ${selectedItems.length > 0 ? 'bg-success-200' : 'bg-neutral-200'}`}></div>
          <div className={`flex items-center ${step === 'select-prompt' ? 'text-primary-600' : selectedPrompt ? 'text-success-600' : 'text-neutral-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step === 'select-prompt' ? 'bg-primary-100 text-primary-600' : 
              selectedPrompt ? 'bg-success-100 text-success-600' : 
              'bg-neutral-100 text-neutral-400'
            }`}>
              2
            </div>
            <span className="ml-2 font-medium">Choose Prompt</span>
          </div>
          <div className={`w-8 h-0.5 ${selectedPrompt ? 'bg-success-200' : 'bg-neutral-200'}`}></div>
          <div className={`flex items-center ${step === 'create-reflection' ? 'text-primary-600' : 'text-neutral-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step === 'create-reflection' ? 'bg-primary-100 text-primary-600' : 'bg-neutral-100 text-neutral-400'
            }`}>
              3
            </div>
            <span className="ml-2 font-medium">Create Reflection</span>
          </div>
        </div>
      </div>

      {/* Step Content */}
      {step === 'select-data' && (
        <div>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-neutral-900 mb-2">
              Select Data to Reflect On
            </h2>
            <p className="text-neutral-600">
              Choose the goals, values, or other data you'd like to include in your reflection.
            </p>
          </div>
          
          <CenterDataSelector
            centerData={centerData}
            selectedItems={selectedItems.map(item => item.id)}
            onSelect={handleDataSelect}
          />
        </div>
      )}

      {step === 'select-prompt' && (
        <div>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-neutral-900 mb-2">
              Choose a Reflection Prompt
            </h2>
            <p className="text-neutral-600">
              Select a prompt that will guide your reflection on the selected data.
            </p>
          </div>
          
          <div className="grid gap-4 md:grid-cols-2">
            {DEFAULT_PROMPTS.map((prompt) => (
              <div
                key={prompt.id}
                className={`
                  p-4 border rounded-lg cursor-pointer transition-all duration-200
                  hover:shadow-md hover:border-primary-500
                  ${selectedPrompt?.id === prompt.id
                    ? 'border-primary-500 bg-primary-50 shadow-md'
                    : 'border-neutral-200 bg-white hover:bg-neutral-50'
                  }
                `}
                onClick={() => handlePromptSelect(prompt)}
              >
                <h3 className="font-medium text-neutral-900 mb-2">
                  {prompt.title}
                </h3>
                <p className="text-sm text-neutral-600 mb-3">
                  {prompt.description}
                </p>
                <p className="text-sm text-neutral-700 italic">
                  "{prompt.prompt}"
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {step === 'create-reflection' && (
        <div>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-neutral-900 mb-2">
              Ready to Create Your Reflection
            </h2>
            <p className="text-neutral-600">
              You've selected {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''} and the "{selectedPrompt?.title}" prompt.
            </p>
          </div>
          
          <div className="bg-neutral-50 rounded-lg p-6 mb-6">
            <h3 className="font-medium text-neutral-900 mb-3">Selected Data:</h3>
            <ul className="space-y-2 mb-4">
              {selectedItems.map((item) => (
                <li key={item.id} className="flex items-center text-sm text-neutral-700">
                  <span className="w-2 h-2 bg-primary-400 rounded-full mr-3"></span>
                  {item.data.title} ({item.type})
                </li>
              ))}
            </ul>
            
            <h3 className="font-medium text-neutral-900 mb-2">Reflection Prompt:</h3>
            <p className="text-sm text-neutral-700 italic">
              "{selectedPrompt?.prompt}"
            </p>
          </div>
          
          <button
            onClick={handleStartReflection}
            className="btn-primary w-full"
          >
            Start Reflection
          </button>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between mt-8">
        <button
          onClick={handlePreviousStep}
          disabled={step === 'select-data'}
          className={`btn-secondary ${step === 'select-data' ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          Previous
        </button>
        
        {step !== 'create-reflection' && (
          <button
            onClick={handleNextStep}
            disabled={
              (step === 'select-data' && selectedItems.length === 0) ||
              (step === 'select-prompt' && !selectedPrompt)
            }
            className={`btn-primary ${
              (step === 'select-data' && selectedItems.length === 0) ||
              (step === 'select-prompt' && !selectedPrompt)
                ? 'opacity-50 cursor-not-allowed'
                : ''
            }`}
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
};