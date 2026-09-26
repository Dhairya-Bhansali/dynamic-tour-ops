import { create } from 'zustand';

interface TripState {
  selectedDestination: any | null;
  selectedExperiences: any[];
  setDestination: (dest: any) => void;
  addExperience: (exp: any) => void;
  removeExperience: (expId: number) => void;
  clearSelection: () => void;
}

export const useTripStore = create<TripState>((set) => ({
  selectedDestination: null,
  selectedExperiences: [],
  setDestination: (dest) => set({ selectedDestination: dest }),
  addExperience: (exp) => set((state) => ({ 
    selectedExperiences: state.selectedExperiences.some(e => e.id === exp.id) 
      ? state.selectedExperiences 
      : [...state.selectedExperiences, exp] 
  })),
  removeExperience: (expId) => set((state) => ({
    selectedExperiences: state.selectedExperiences.filter(e => e.id !== expId)
  })),
  clearSelection: () => set({ selectedDestination: null, selectedExperiences: [] })
}));
