import React from "react";

export const ModelSelector: React.FC<{ selected: string; onChange: (val: string) => void }> = ({ selected, onChange }) => (
  <select value={selected} onChange={(e) => onChange(e.target.value)} className="p-2 border rounded bg-background">
    <option value="gpt-4o">GPT-4o</option>
    <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
  </select>
);
