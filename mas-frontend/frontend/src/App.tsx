import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import { ChatProvider } from './contexts/ChatContext';
import { AgentTrackingProvider } from './contexts/AgentTrackingContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { SplitLayout } from './components/Layout/SplitLayout';
import { ChatInterface } from './components/Chat/ChatInterface';
import { AgentResponsePanel } from './components/AgentPanel/AgentResponsePanel';
import { Header } from './components/Layout/Header';
import { theme } from './styles/theme';

import './styles/main.scss';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <WebSocketProvider>
          <ChatProvider>
            <AgentTrackingProvider>
              <div className="app-container">
                <Header />
                <SplitLayout
                  left={<ChatInterface />}
                  right={<AgentResponsePanel />}
                />
              </div>
            </AgentTrackingProvider>
          </ChatProvider>
        </WebSocketProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;