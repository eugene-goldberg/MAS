// Agent color mapping
export const getAgentColor = (agentName: string): string => {
  const colorMap: Record<string, string> = {
    'Weather Agent': '#3498db',
    'RAG Agent': '#9b59b6',
    'Academic WebSearch': '#e74c3c',
    'Academic NewResearch': '#e67e22',
    'Greeter Agent': '#2ecc71',
    'MAS Coordinator': '#34495e'
  };
  
  return colorMap[agentName] || '#95a5a6';
};

// Agent icon mapping
export const getAgentIcon = (agentName: string): string => {
  const iconMap: Record<string, string> = {
    'Weather Agent': '🌤️',
    'RAG Agent': '📚',
    'Academic WebSearch': '🔍',
    'Academic NewResearch': '🔬',
    'Greeter Agent': '👋',
    'MAS Coordinator': '🤖'
  };
  
  return iconMap[agentName] || '🤖';
};

// Format duration from milliseconds
export const formatDuration = (ms: number): string => {
  if (ms < 1000) {
    return `${ms}ms`;
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(1)}s`;
  } else {
    return `${(ms / 60000).toFixed(1)}m`;
  }
};

// Format date/time
export const formatTime = (date: Date): string => {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// Truncate text
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};