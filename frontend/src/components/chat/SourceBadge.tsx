import React from "react";

export const SourceBadge: React.FC<{ sourceName: string }> = ({ sourceName }) => (
  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 mr-1">
    📄 {sourceName}
  </span>
);
