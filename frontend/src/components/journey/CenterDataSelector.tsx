import React from 'react';
import { DataItem, DataCategory } from './DataItem';

interface CenterData {
  user_id: string;
  goals: any[];
  values: any[];
  energy_logs: any[];
  documents: any[];
  assessments: any[];
  data_summary: Record<string, number>;
}

interface CenterDataSelectorProps {
  centerData: CenterData;
  selectedItems: string[];
  onSelect: (id: string, data: any, type: string) => void;
}

export const CenterDataSelector: React.FC<CenterDataSelectorProps> = ({
  centerData,
  selectedItems,
  onSelect,
}) => {
  const handleGoalSelect = (id: string, data: any) => {
    onSelect(id, data, 'goal');
  };

  const handleValueSelect = (id: string, data: any) => {
    onSelect(id, data, 'value');
  };

  const handleEnergyLogSelect = (id: string, data: any) => {
    onSelect(id, data, 'energy_log');
  };

  const handleDocumentSelect = (id: string, data: any) => {
    onSelect(id, data, 'document');
  };

  const handleAssessmentSelect = (id: string, data: any) => {
    onSelect(id, data, 'assessment');
  };

  return (
    <div className="space-y-6">
      {/* Goals Section */}
      <DataCategory
        title="Goals"
        description="Select goals you'd like to reflect on"
        itemCount={centerData.goals.length}
      >
        {centerData.goals.length > 0 ? (
          centerData.goals.map((goal, index) => (
            <DataItem
              key={goal.id || `goal-${index}`}
              id={goal.id || `goal-${index}`}
              title={goal.title || 'Untitled Goal'}
              description={goal.description}
              status={goal.status}
              onClick={handleGoalSelect}
              data={goal}
              isSelected={selectedItems.includes(goal.id || `goal-${index}`)}
            />
          ))
        ) : (
          <div className="text-center py-8 text-neutral-500">
            <div className="mb-2">
              <svg className="w-12 h-12 mx-auto text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <p>No goals found. Create some goals first to reflect on them.</p>
          </div>
        )}
      </DataCategory>

      {/* Values Section - Placeholder */}
      <DataCategory
        title="Values"
        description="Select values you'd like to reflect on"
        itemCount={centerData.values.length}
      >
        <div className="text-center py-8 text-neutral-500">
          <div className="mb-2">
            <svg className="w-12 h-12 mx-auto text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <p>Values reflection coming soon.</p>
        </div>
      </DataCategory>

      {/* Energy Logs Section - Placeholder */}
      <DataCategory
        title="Energy Logs"
        description="Select energy logs you'd like to reflect on"
        itemCount={centerData.energy_logs.length}
      >
        <div className="text-center py-8 text-neutral-500">
          <div className="mb-2">
            <svg className="w-12 h-12 mx-auto text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <p>Energy logs reflection coming soon.</p>
        </div>
      </DataCategory>

      {/* Documents Section - Placeholder */}
      <DataCategory
        title="Documents"
        description="Select documents you'd like to reflect on"
        itemCount={centerData.documents.length}
      >
        <div className="text-center py-8 text-neutral-500">
          <div className="mb-2">
            <svg className="w-12 h-12 mx-auto text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p>Document reflection coming soon.</p>
        </div>
      </DataCategory>

      {/* Assessments Section - Placeholder */}
      <DataCategory
        title="Assessments"
        description="Select assessments you'd like to reflect on"
        itemCount={centerData.assessments.length}
      >
        <div className="text-center py-8 text-neutral-500">
          <div className="mb-2">
            <svg className="w-12 h-12 mx-auto text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <p>Assessment reflection coming soon.</p>
        </div>
      </DataCategory>
    </div>
  );
};