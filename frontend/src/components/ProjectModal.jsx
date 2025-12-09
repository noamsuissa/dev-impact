import React, { useState, useEffect, useRef } from 'react';
import { X, Upload, Trash2, Image as ImageIcon, Loader2 } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';
import { projects } from '../utils/client';

const ProjectModal = ({ isOpen, onClose, project, onEdit, onDelete, readOnly = false }) => {
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [totalSize, setTotalSize] = useState(0);
  const sizeLimit = 50 * 1024 * 1024; // 50MB default
  const [selectedImage, setSelectedImage] = useState(null);
  const fileInputRef = useRef(null);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    if (isOpen && project?.id) {
      fetchEvidence();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, project?.id]);

  const fetchEvidence = async () => {
    if (!project?.id) return;
    
    // If read-only and evidence is already in project data, use it
    if (readOnly && project.evidence) {
      setEvidence(project.evidence || []);
      const total = (project.evidence || []).reduce((sum, e) => sum + (e.file_size || 0), 0);
      setTotalSize(total);
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const evidenceList = await projects.getEvidence(project.id);
      setEvidence(evidenceList || []);
      
      // Calculate total size
      const total = (evidenceList || []).reduce((sum, e) => sum + (e.file_size || 0), 0);
      setTotalSize(total);
    } catch (err) {
      // For read-only mode, don't show error if evidence fetch fails
      if (!readOnly) {
        setError(err.message || 'Failed to load evidence');
      }
      setEvidence([]);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const getImageUrl = (evidenceItem) => {
    // Use the URL provided by the backend, or fallback to file_path if URL not available
    return evidenceItem?.url || '';
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Only image files are allowed');
      return;
    }

    // Validate file size (check against remaining quota)
    const remainingSpace = sizeLimit - totalSize;
    if (file.size > remainingSpace) {
      setError(`File size (${formatFileSize(file.size)}) exceeds remaining space (${formatFileSize(remainingSpace)})`);
      return;
    }

    setUploading(true);
    setError(null);

    try {
      // Single-step flow: upload file and create evidence record via backend
      await projects.uploadEvidence(project.id, file);

      // Refresh evidence list
      await fetchEvidence();
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err.message || 'Failed to upload screenshot');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteEvidence = async (evidenceId) => {
    if (!confirm('Are you sure you want to delete this screenshot?')) return;

    setDeletingId(evidenceId);
    setError(null);

    try {
      await projects.deleteEvidence(project.id, evidenceId);
      await fetchEvidence();
    } catch (err) {
      setError(err.message || 'Failed to delete screenshot');
    } finally {
      setDeletingId(null);
    }
  };

  const handleImageClick = (evidenceItem) => {
    setSelectedImage(evidenceItem);
  };

  if (!isOpen || !project) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            onClose();
          }
        }}
      >
        <div className="bg-terminal-bg border border-terminal-border max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-terminal-border">
            <div className="text-lg text-terminal-orange font-mono">
              &gt; Project Details
            </div>
            <button
              onClick={onClose}
              className="text-terminal-gray hover:text-terminal-orange transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto overflow-x-hidden p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 min-w-0">
              {/* Left: Project Display */}
              <div className="space-y-4 min-w-0">
                <div className="bg-terminal-bg-lighter border border-terminal-border p-4 overflow-x-auto">
                  <ProjectCard project={project} compact={true} />
                </div>
              </div>

              {/* Right: Details and Evidence */}
              <div className="space-y-4">
                {/* Actions */}
                {!readOnly && (
                  <div className="bg-terminal-bg-lighter border border-terminal-border p-4 space-y-3">
                    <div className="text-sm text-terminal-orange font-mono">
                      &gt; Actions
                    </div>
                    <div className="flex gap-2">
                      {onEdit && (
                        <TerminalButton onClick={() => { onEdit(project); onClose(); }}>
                          [Edit]
                        </TerminalButton>
                      )}
                      {onDelete && (
                        <TerminalButton onClick={() => { onDelete(project.id); onClose(); }}>
                          [Delete]
                        </TerminalButton>
                      )}
                    </div>
                  </div>
                )}

                {/* Evidence Section */}
                <div className="bg-terminal-bg-lighter border border-terminal-border p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-terminal-orange font-mono">
                      &gt; Screenshots
                    </div>
                    {!readOnly && (
                      <div className="text-xs text-terminal-gray">
                        {formatFileSize(totalSize)} / {formatFileSize(sizeLimit)}
                      </div>
                    )}
                  </div>

                  {error && (
                    <div className="text-red-400 text-sm">
                      ✗ {error}
                    </div>
                  )}

                  {/* Upload Button */}
                  {!readOnly && (
                    <div>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="hidden"
                        id="evidence-upload"
                        disabled={uploading}
                      />
                      <TerminalButton
                        onClick={() => {
                          if (!uploading && totalSize < sizeLimit) {
                            fileInputRef.current?.click();
                          }
                        }}
                        disabled={uploading || (totalSize >= sizeLimit)}
                        className="inline-flex items-center gap-2"
                      >
                        {uploading ? (
                          <>
                            <Loader2 size={16} className="animate-spin" />
                            [Uploading...]
                          </>
                        ) : (
                          <>
                            <Upload size={16} />
                            [Upload Screenshot]
                          </>
                        )}
                      </TerminalButton>
                    </div>
                  )}

                  {/* Evidence List */}
                  {loading ? (
                    <div className="text-terminal-gray text-sm">Loading...</div>
                  ) : evidence.length === 0 ? (
                    <div className="text-terminal-gray text-sm">
                      No screenshots yet. {!readOnly && 'Upload one to get started!'}
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-3">
                      {evidence.map((item) => (
                        <div
                          key={item.id}
                          className="relative group border border-terminal-border bg-terminal-bg hover:border-terminal-orange/50 transition-colors cursor-pointer"
                          onClick={() => handleImageClick(item)}
                        >
                          <img
                            src={getImageUrl(item)}
                            alt={item.file_name}
                            className="w-full h-32 object-cover"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'flex';
                            }}
                          />
                          <div className="hidden absolute inset-0 items-center justify-center bg-terminal-bg-lighter">
                            <ImageIcon size={32} className="text-terminal-gray" />
                          </div>
                          {!readOnly && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteEvidence(item.id);
                              }}
                              disabled={deletingId === item.id}
                              className="absolute top-1 right-1 p-1 bg-red-500/80 hover:bg-red-500 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                              title="Delete"
                            >
                              {deletingId === item.id ? (
                                <Loader2 size={12} className="animate-spin" />
                              ) : (
                                <Trash2 size={12} />
                              )}
                            </button>
                          )}
                          <div className="absolute bottom-0 left-0 right-0 bg-black/70 p-1 text-xs text-white truncate">
                            {item.file_name}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Image Lightbox */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/90 flex items-center justify-center z-[60] p-4"
          onClick={() => setSelectedImage(null)}
        >
          <button
            onClick={() => setSelectedImage(null)}
            className="absolute top-4 right-4 text-white hover:text-terminal-orange"
          >
            <X size={24} />
          </button>
          <img
            src={getImageUrl(selectedImage)}
            alt={selectedImage.file_name}
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
};

export default ProjectModal;

