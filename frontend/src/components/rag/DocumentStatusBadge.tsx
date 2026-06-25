import React from "react";

export const DocumentStatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const colors: Record<string, string> = {
    indexed: "bg-green-500/10 text-green-400 border-green-500/20",
    processing: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    failed: "bg-red-500/10 text-red-400 border-red-500/20",
  };
  return (
    <span className={`px-2 py-1 rounded text-xs border ${colors[status] || "bg-gray-500/10"}`}>
      {status}
    </span>
  );
};


// Add accessible aria labels
export default DocumentStatusBadge;
