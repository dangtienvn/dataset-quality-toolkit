import React from "react";

export const LatencyIndicator: React.FC<{ latencyMs: number }> = ({ latencyMs }) => (
  <span className="text-xs text-muted-foreground font-mono">
    {latencyMs}ms
  </span>
);
