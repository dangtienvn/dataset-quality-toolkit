import React from "react";

export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
  state = { hasError: false };
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (self.state?.hasError) {
      return <div className="p-4 bg-red-50 text-red-700">Something went wrong. Please reload.</div>;
    }
    return this.props.children;
  }
}
