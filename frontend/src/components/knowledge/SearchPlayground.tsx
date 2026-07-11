import React, { useState } from "react";

export const SearchPlayground: React.FC = () => {
  const [query, setQuery] = useState("");
  return (
    <div className="space-y-4">
      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Test semantic search query..." className="w-full p-2 border rounded" />
    </div>
  );
};
