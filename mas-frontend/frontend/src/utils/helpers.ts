import { v4 as uuidv4 } from 'uuid';

// Generate unique session ID
export const generateSessionId = (): string => {
  return uuidv4();
};

// Download blob as file
export const downloadBlob = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Export chat history
export const exportChatHistory = (data: any): void => {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json'
  });
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  downloadBlob(blob, `mas-chat-export-${timestamp}.json`);
};

// Debounce function
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// Check if object is empty
export const isEmpty = (obj: any): boolean => {
  return Object.keys(obj).length === 0;
};