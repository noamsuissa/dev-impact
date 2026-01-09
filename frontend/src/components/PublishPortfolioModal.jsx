import React, { useState } from 'react';
import { X } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import TerminalSelect from './common/TerminalSelect';

const PublishPortfolioModal = ({ isOpen, onClose, portfolios = [], onPublish, publishedPortfolioSlugs = [] }) => {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null);
  const [isPublishing, setIsPublishing] = useState(false);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    if (isOpen) {
      setSelectedPortfolioId(null);
      setError(null);
      setIsPublishing(false);
    }
  }, [isOpen]);

  const handlePublish = async () => {
    if (!selectedPortfolioId) {
      setError('Please select a portfolio to publish');
      return;
    }

    setIsPublishing(true);
    setError(null);

    try {
      await onPublish(selectedPortfolioId);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to publish portfolio');
    } finally {
      setIsPublishing(false);
    }
  };

  if (!isOpen) return null;

  const availablePortfolios = portfolios.filter(p => !publishedPortfolioSlugs.includes(p.slug));

  // Convert portfolios to options format for TerminalSelect
  const portfolioOptions = availablePortfolios.map(p => ({
    value: p.id,
    label: `${p.name}${p.description ? ` - ${p.description}` : ''}`
  }));

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-terminal-bg border border-terminal-border p-6 max-w-md w-full">
        <div className="flex items-center justify-between mb-6">
          <div className="text-lg text-terminal-orange">
            Publish Portfolio
          </div>
          <button
            onClick={onClose}
            className="text-terminal-gray hover:text-terminal-orange transition-colors"
            disabled={isPublishing}
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          {availablePortfolios.length === 0 ? (
            <div className="text-terminal-gray text-sm">
              All portfolios are already published. Unpublish a portfolio first to republish it.
            </div>
          ) : (
            <>
              <div>
                <label className="block text-sm text-terminal-gray mb-2">
                  Select Portfolio to Publish *
                </label>
                <TerminalSelect
                  value={selectedPortfolioId}
                  onChange={(value) => {
                    setSelectedPortfolioId(value);
                    setError(null);
                  }}
                  options={portfolioOptions}
                  placeholder="-- Select Portfolio --"
                  disabled={isPublishing}
                />
              </div>

              {error && (
                <div className="text-red-400 text-sm">
                  ✗ {error}
                </div>
              )}

              <div className="flex gap-3 justify-end pt-4">
                <TerminalButton
                  type="button"
                  onClick={onClose}
                  disabled={isPublishing}
                >
                  [Cancel]
                </TerminalButton>
                <TerminalButton
                  type="button"
                  onClick={handlePublish}
                  disabled={isPublishing || !selectedPortfolioId}
                >
                  {isPublishing ? '[Publishing...]' : '[Publish]'}
                </TerminalButton>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PublishPortfolioModal;
