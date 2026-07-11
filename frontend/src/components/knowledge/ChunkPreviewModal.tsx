import React from "react";

export const ChunkPreviewModal: React.FC<{ isOpen: boolean; chunkText: string }> = ({ isOpen, chunkText }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-background p-6 rounded-lg max-w-lg w-full">
        <h4 className="font-bold mb-2">Chunk Details</h4>
        <p className="text-sm">{chunkText}</p>
      </div>
    </div>
  );
};
