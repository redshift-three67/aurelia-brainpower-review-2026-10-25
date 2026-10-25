import { useState, useEffect } from 'react';

const STORAGE_KEY = 'wordEnergyHistory';
const MAX_HISTORY_ITEMS = 20;

export const useWordEnergyHistory = () => {
  const [history, setHistory] = useState<string[]>([]);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setHistory(Array.isArray(parsed) ? parsed : []);
      }
    } catch (error) {
      console.error('Failed to load word energy history:', error);
    }
  }, []);

  const addToHistory = (word: string) => {
    const trimmedWord = word.trim().toUpperCase();
    if (!trimmedWord) return;

    setHistory(prev => {
      // Remove duplicates and add to front
      const filtered = prev.filter(item => item !== trimmedWord);
      const updated = [trimmedWord, ...filtered].slice(0, MAX_HISTORY_ITEMS);
      
      // Save to localStorage
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (error) {
        console.error('Failed to save word energy history:', error);
      }
      
      return updated;
    });
  };

  const clearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear word energy history:', error);
    }
  };

  return { history, addToHistory, clearHistory };
};
