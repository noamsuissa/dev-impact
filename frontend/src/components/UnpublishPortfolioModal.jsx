import React, { useState } from 'react';
import { X } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import TerminalSelect from './common/TerminalSelect';

const UnpublishPortfolioModal = ({ isOpen, onClose, portfolios = [], onUnpublish, publishedPortfolioSlugs = [] }) => {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null);
  const [isUnpublishing, setIsUnpublishing] = useState(false);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    if (isOpen) {
      setSelectedPortfolioId(null);
      setError(null);
      setIsUnpublishing(false);
    }
  }, [isOpen]);

  const handleUnpublish = async () => {
    if (!selectedPortfolioId) {
      setError('Please select a portfolio to unpublish');
      return;
    }

    setIsUnpublishing(true);
    setError(null);

    try {
      await onUnpublish(selectedPortfolioId);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to unpublish portfolio');
    } finally {
      setIsUnpublishing(false);
    }
  };

  if (!isOpen) return null;

  const publishedPortfolios = portfolios.filter(p => publishedPortfolioSlugs.includes(p.slug));

  // Convert portfolios to options format for TerminalSelect
  const portfolioOptions = publishedPortfolios.map(p => ({
    value: p.id,
    label: `${p.name}${p.description ? ` - ${p.description}` : ''}`
  }));

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-terminal-bg border border-terminal-border p-6 max-w-md w-full">
        <div className="flex items-center justify-between mb-6">
          <div className="text-lg text-terminal-orange">
            Unpublish Portfolio
          </div>
          <button
            onClick={onClose}
            className="text-terminal-gray hover:text-terminal-orange transition-colors"
            disabled={isUnpublishing}
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          {publishedPortfolios.length === 0 ? (
            <div className="text-terminal-gray text-sm">
              No portfolios are currently published.
            </div>
          ) : (
            <>
              <div>
                <label className="block text-sm text-terminal-gray mb-2">
                  Select Portfolio to Unpublish *
                </label>
                <TerminalSelect
                  value={selectedPortfolioId}
                  onChange={(value) => {
                    setSelectedPortfolioId(value);
                    setError(null);
                  }}
                  options={portfolioOptions}
                  placeholder="-- Select Portfolio --"
                  disabled={isUnpublishing}
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
                  disabled={isUnpublishing}
                >
                  [Cancel]
                </TerminalButton>
                <TerminalButton
                  type="button"
                  onClick={handleUnpublish}
                  disabled={isUnpublishing || !selectedPortfolioId}
                >
                  {isUnpublishing ? '[Unpublishing...]' : '[Unpublish]'}
                </TerminalButton>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default UnpublishPortfolioModal;
