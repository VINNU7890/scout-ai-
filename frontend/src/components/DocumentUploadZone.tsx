import React, { useRef, useState } from "react";
import { Upload, FileText, X, Loader2 } from "lucide-react";
import { uploadDocument, deleteDocument } from "../services/api";
import { UploadedDocumentItem } from "../types";
import { useAppStore } from "../store/useAppStore";

interface DocumentUploadZoneProps {
  uploadedDocs?: UploadedDocumentItem[];
  onUploadSuccess?: (doc: UploadedDocumentItem) => void;
  onRemove?: (docId: string) => void;
}

export const DocumentUploadZone: React.FC<DocumentUploadZoneProps> = ({
  uploadedDocs: propDocs,
  onUploadSuccess: propOnSuccess,
  onRemove: propOnRemove,
}) => {
  const store = useAppStore();
  const uploadedDocs = propDocs ?? store.uploadedDocuments;
  const onUploadSuccess = propOnSuccess ?? store.addUploadedDocument;
  const onRemove = propOnRemove ?? ((id: string) => {
    deleteDocument(id).catch(() => {});
    store.removeUploadedDocument(id);
  });

  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setErrorMsg(null);
    setIsUploading(true);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const res = await uploadDocument(file);
        onUploadSuccess(res);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to upload document");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="space-y-3">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          isDragging
            ? "border-brand-500 bg-brand-500/10 scale-[1.01]"
            : "border-border hover:border-brand-500/50 bg-background/50 hover:bg-muted/40"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="flex flex-col items-center justify-center space-y-2">
          {isUploading ? (
            <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
          ) : (
            <div className="w-10 h-10 rounded-full bg-brand-500/10 flex items-center justify-center text-brand-500">
              <Upload className="w-5 h-5" />
            </div>
          )}
          <div>
            <p className="text-xs font-semibold text-foreground">
              {isUploading ? "Uploading & chunking vector embeddings..." : "Click or drag internal docs to upload"}
            </p>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Supports PDF, DOCX, TXT, and Markdown (up to 25MB each)
            </p>
          </div>
        </div>
      </div>

      {errorMsg && (
        <p className="text-xs text-red-500 font-medium px-1">{errorMsg}</p>
      )}

      {/* Uploaded Documents List */}
      {uploadedDocs.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            Uploaded ({uploadedDocs.length}):
          </p>
          <div className="flex flex-wrap gap-2">
            {uploadedDocs.map((doc) => (
              <div
                key={doc.id}
                className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-card border border-border text-xs shadow-sm"
              >
                <FileText className="w-3.5 h-3.5 text-brand-500" />
                <span className="font-medium text-foreground max-w-[160px] truncate" title={doc.filename}>
                  {doc.filename}
                </span>
                <span className="text-[10px] text-muted-foreground">
                  ({formatFileSize(doc.file_size_bytes)})
                </span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemove(doc.id);
                  }}
                  className="p-0.5 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
