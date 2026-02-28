'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * Error boundary for ChatKit widget to catch and display errors gracefully
 */
export class ChatKitErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('[ChatKit Error Boundary]', error);
    console.error('[ChatKit Error Boundary] Component Stack:', errorInfo.componentStack);
    console.error('[ChatKit Error Boundary] Error Details:', {
      message: error.message,
      stack: error.stack,
      name: error.name
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          position: 'fixed',
          bottom: '10px',
          right: '10px',
          background: '#ff4444',
          color: 'white',
          padding: '12px',
          borderRadius: '6px',
          zIndex: 99999,
          fontSize: '12px',
          maxWidth: '350px',
          fontFamily: 'monospace',
        }}>
          <div style={{ marginBottom: '8px' }}>
            <strong>ChatKit Error:</strong>
          </div>
          <div style={{ marginBottom: '8px' }}>
            {this.state.error?.message || 'Unknown error'}
          </div>
          <div style={{ fontSize: '10px', opacity: 0.8 }}>
            Check console for details
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
