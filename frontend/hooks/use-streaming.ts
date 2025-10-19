import { useCallback, useRef } from 'react';

export const useStreaming = () => {
  const contentRef = useRef<string>('');
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const updateStreamingContent = useCallback((
    newChunk: string,
    updateCallback: (content: string) => void
  ) => {
    // Add the new chunk to our content
    contentRef.current += newChunk;
    
    // Clear any pending update
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    // Update immediately for better UX
    updateCallback(contentRef.current);

    // Also schedule a debounced update as backup
    updateTimeoutRef.current = setTimeout(() => {
      updateCallback(contentRef.current);
    }, 50);
  }, []);

  const resetStreamingContent = useCallback(() => {
    contentRef.current = '';
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
      updateTimeoutRef.current = null;
    }
  }, []);

  const getStreamingContent = useCallback(() => {
    return contentRef.current;
  }, []);

  return {
    updateStreamingContent,
    resetStreamingContent,
    getStreamingContent,
  };
};