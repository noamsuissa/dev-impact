import React, { useState } from 'react';
import { X } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import TerminalSelect from './common/TerminalSelect';

const PortfolioSelectionModal = ({ isOpen, onClose, portfolios = [], onSelect }) => {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    if (isOpen) {
      setSelectedPortfolioId(null);
      setError(null);
    }
  }, [isOpen]);

  const handleSelect = () => {
    if (!selectedPortfolioId) {
      setError('Please select a portfolio to export');
      return;
    }

    const selectedPortfolio = portfolios.find(p => p.id === selectedPortfolioId);
    if (selectedPortfolio) {
      onSelect(selectedPortfolio);
      onClose();
    }
  };

  if (!isOpen) return null;

  // Convert portfolios to options format for TerminalSelect
  const portfolioOptions = portfolios.map(p => ({
    value: p.id,
    label: `${p.name}${p.description ? ` - ${p.description}` : ''}`
  }));

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-terminal-bg border border-terminal-border p-6 max-w-md w-full">
        <div className="flex items-center justify-between mb-6">
          <div className="text-lg text-terminal-orange">
            Select Portfolio to Export
          </div>
          <button
            onClick={onClose}
            className="text-terminal-gray hover:text-terminal-orange transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          {portfolios.length === 0 ? (
            <div className="text-terminal-gray text-sm">
              No portfolios available. Create a portfolio first.
            </div>
          ) : (
            <>
              <div>
                <label className="block text-sm text-terminal-gray mb-2">
                  Select Portfolio *
                </label>
                <TerminalSelect
                  value={selectedPortfolioId}
                  onChange={(value) => {
                    setSelectedPortfolioId(value);
                    setError(null);
                  }}
                  options={portfolioOptions}
                  placeholder="-- Select Portfolio --"
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
                >
                  [Cancel]
                </TerminalButton>
                <TerminalButton
                  type="button"
                  onClick={handleSelect}
                  disabled={!selectedPortfolioId}
                >
                  [Export]
                </TerminalButton>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PortfolioSelectionModal;

