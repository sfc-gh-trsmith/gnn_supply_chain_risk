import { create } from 'zustand'
import type { CortexMessage } from '../types/cortex'
import type { Bottleneck, Vendor } from '../types/risk'

interface AppState {
  messages: CortexMessage[]
  pendingPrompt: string | null
  chatContext: string
  isChatOpen: boolean
  
  selectedBottleneck: Bottleneck | null
  selectedVendor: Vendor | null
  selectedRegion: string | null
  
  persona: 'executive' | 'operational' | 'technical'

  addMessage: (message: CortexMessage) => void
  updateMessage: (id: string, updates: Partial<CortexMessage>) => void
  clearMessages: () => void
  setPendingPrompt: (prompt: string | null) => void
  setChatContext: (context: string) => void
  setIsChatOpen: (open: boolean) => void
  setSelectedBottleneck: (bottleneck: Bottleneck | null) => void
  setSelectedVendor: (vendor: Vendor | null) => void
  setSelectedRegion: (region: string | null) => void
  setPersona: (persona: 'executive' | 'operational' | 'technical') => void
}

export const useAppStore = create<AppState>((set) => ({
  messages: [],
  pendingPrompt: null,
  chatContext: '',
  isChatOpen: false,
  
  selectedBottleneck: null,
  selectedVendor: null,
  selectedRegion: null,
  
  persona: 'operational',

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, ...updates } : m
      ),
    })),

  clearMessages: () => set({ messages: [] }),

  setPendingPrompt: (prompt) => set({ pendingPrompt: prompt }),

  setChatContext: (context) => set({ chatContext: context }),

  setIsChatOpen: (open) => set({ isChatOpen: open }),
  
  setSelectedBottleneck: (bottleneck) => set({ selectedBottleneck: bottleneck }),
  
  setSelectedVendor: (vendor) => set({ selectedVendor: vendor }),
  
  setSelectedRegion: (region) => set({ selectedRegion: region }),
  
  setPersona: (persona) => set({ persona }),
}))
