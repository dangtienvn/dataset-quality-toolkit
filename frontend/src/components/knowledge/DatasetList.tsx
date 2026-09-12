import React from "react";
import { DatasetCard } from "./DatasetCard";

export const DatasetList: React.FC<{ items: any[] }> = ({ items }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
    {items.map((item) => (
      <DatasetCard key={item.id} name={item.name} description={item.description} />
    ))}
  </div>
);

# Updated audit checkpoint 2026-09-12 14:15
