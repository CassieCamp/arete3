"use client";

import { createContext, useContext, useState, ReactNode } from 'react';
import { UnifiedEntryModal } from '@/components/entries/UnifiedEntryModal';
import { useEntryService, FreemiumStatus } from '@/services/entryService';

interface EntryModalContextType {
  openEntryModal: () => void;
  closeEntryModal: () => void;
  isOpen: boolean;
}

const EntryModalContext = createContext<EntryModalContextType | undefined>(undefined);

export function EntryModalProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [freemiumStatus, setFreemiumStatus] = useState<FreemiumStatus>({
    has_coach: false,
    entries_count: 0,
    max_free_entries: 5,
    entries_remaining: 3,
    can_create_entries: true,
    can_access_insights: false,
    is_freemium: true
  });
  
  const entryService = useEntryService();

  const openEntryModal = async () => {
    try {
      const status = await entryService.getFreemiumStatus();
      setFreemiumStatus(status);
      setIsOpen(true);
    } catch (error) {
      console.error('Error fetching freemium status:', error);
      setIsOpen(true); // Open anyway with default status
    }
  };

  const closeEntryModal = () => {
    setIsOpen(false);
  };

  return (
    <EntryModalContext.Provider value={{ openEntryModal, closeEntryModal, isOpen }}>
      {children}
      <UnifiedEntryModal
        isOpen={isOpen}
        onClose={closeEntryModal}
        freemiumStatus={freemiumStatus}
      />
    </EntryModalContext.Provider>
  );
}

export function useEntryModal() {
  const context = useContext(EntryModalContext);
  if (context === undefined) {
    throw new Error('useEntryModal must be used within an EntryModalProvider');
  }
  return context;
}