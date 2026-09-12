import React from "react";

export const DatasetCard: React.FC<{ name: string; description?: string }> = ({ name, description }) => (
  <div className="p-4 border rounded-lg bg-card text-card-foreground shadow-sm">
    <h3 className="text-lg font-semibold">{name}</h3>
    <p className="text-sm text-muted-foreground">{description || "No description provided."}</p>
  </div>
);

# Updated audit checkpoint 2026-09-12 09:30
