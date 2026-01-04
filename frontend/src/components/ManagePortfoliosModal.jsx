import React, { useState } from 'react';
import { X, Trash2, Eye } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import DeletePortfolioModal from './DeletePortfolioModal';

const ManagePortfoliosModal = ({ 
  isOpen, 
  onClose, 
  portfolios = [], 
  onDeletePortfolio, 
  onEditPortfolio,
  publishedPortfolioSlugs = [],
  portfolioViewCounts = {},
  projects = []
}) => {
  const [deletingPortfolio, setDeletingPortfolio] = useState(null);

  React.useEffect(() => {
    if (isOpen) {
      setDeletingPortfolio(null);
    }
  }, [isOpen]);

  const handleDeleteClick = (portfolio) => {
    setDeletingPortfolio(portfolio);
  };

  const handleDeleteConfirm = async (portfolioId) => {
    await onDeletePortfolio(portfolioId);
    setDeletingPortfolio(null);
  };

  const handleCloseDeleteModal = () => {
    setDeletingPortfolio(null);
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className="bg-terminal-bg border border-terminal-border p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="text-lg text-terminal-orange">
              Manage Portfolios
            </div>
            <button
              onClick={onClose}
              className="text-terminal-gray hover:text-terminal-orange transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          <div className="space-y-3">
            {portfolios.length === 0 ? (
              <div className="text-terminal-gray text-sm text-center py-8">
                No portfolios yet. Create one to get started!
              </div>
            ) : (
              portfolios.map((portfolio) => {
                const isPublished = publishedPortfolioSlugs.includes(portfolio.slug);
                const projectCount = projects.filter(p => p.portfolio_id === portfolio.id).length;
                const viewCount = portfolioViewCounts[portfolio.slug] || 0;

                return (
                  <div
                    key={portfolio.id}
                    className="bg-terminal-bg-lighter border border-terminal-border p-4 rounded flex items-center justify-between hover:border-terminal-orange/50 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-terminal-orange font-semibold">
                          {portfolio.name}
                        </span>
                        {isPublished && (
                          <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                          </span>
                        )}
                      </div>
                      {portfolio.description && (
                        <div className="text-terminal-gray text-sm mb-2">
                          {portfolio.description}
                        </div>
                      )}
                      <div className="text-terminal-gray text-xs flex items-center gap-2">
                        <span>{projectCount} project{projectCount !== 1 ? 's' : ''} assigned</span>
                        {isPublished && <span>• Published</span>}
                        {viewCount > 0 && (
                          <span className="flex items-center gap-1">
                            <Eye size={12} />
                            <span>{viewCount} view{viewCount !== 1 ? 's' : ''}</span>
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      {onEditPortfolio && (
                        <button
                          onClick={() => {
                            onEditPortfolio(portfolio);
                            onClose();
                          }}
                          className="px-3 py-1.5 bg-terminal-bg border border-terminal-border hover:border-terminal-orange text-terminal-orange text-sm transition-colors"
                          title="Edit portfolio"
                        >
                          Edit
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteClick(portfolio)}
                        className="px-3 py-1.5 bg-red-500/20 border border-red-500/50 hover:bg-red-500/30 text-red-400 transition-colors flex items-center gap-2"
                        title="Delete portfolio"
                      >
                        <Trash2 size={14} />
                        Delete
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <div className="flex justify-end pt-6 mt-6 border-t border-terminal-border">
            <TerminalButton onClick={onClose}>
              [Close]
            </TerminalButton>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deletingPortfolio && (
        <DeletePortfolioModal
          isOpen={!!deletingPortfolio}
          onClose={handleCloseDeleteModal}
          portfolio={deletingPortfolio}
          onDelete={handleDeleteConfirm}
          projectCount={projects.filter(p => p.portfolio_id === deletingPortfolio.id).length}
        />
      )}
    </>
  );
};

export default ManagePortfoliosModal;

