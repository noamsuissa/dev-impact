import React from 'react';
import { Plus, Sparkles } from 'lucide-react';

const PortfolioTabs = ({ portfolios, selectedPortfolioId, onSelectPortfolio, onAddPortfolio, onManagePortfolios, publishedProfileSlugs = [], canAddProfile = true, onUpgradeClick }) => {
  if (!portfolios || portfolios.length === 0) {
    return (
      <div className="mb-5">
        <div className="flex items-center gap-2">
          <button
            onClick={canAddProfile ? onAddPortfolio : onUpgradeClick}
            className={`px-3 py-1.5 border text-sm transition-colors flex items-center gap-2 ${canAddProfile
                ? 'bg-terminal-bg-lighter border-terminal-border hover:border-terminal-orange text-terminal-orange'
                : 'bg-terminal-bg-lighter border-terminal-border text-terminal-orange cursor-pointer hover:border-terminal-orange opacity-70 hover:opacity-100'
              }`}
            title={!canAddProfile ? 'Portfolio limit reached. Click to upgrade to Pro for unlimited portfolios.' : ''}
          >
            {canAddProfile ? <Plus size={14} /> : <Sparkles size={14} className="animate-pulse" />}
            Add Portfolio
          </button>
          <span className="text-terminal-gray text-sm">No portfolios yet. Create one to organize your projects.</span>
        </div>
      </div>
    );
  }

  const hasActiveTab = selectedPortfolioId !== null;

  return (
    <div className="mb-5">
      <div className="relative">
        <div className="flex items-end gap-0 overflow-x-auto">
          <div className="flex items-end gap-0 relative">
            {portfolios.map((portfolio, index) => {
              const isActive = portfolio.id === selectedPortfolioId;
              const isPublished = publishedProfileSlugs.includes(portfolio.slug);

              return (
                <div key={portfolio.id} className="relative">
                  {/* Tab */}
                  <button
                    onClick={() => onSelectPortfolio(portfolio.id)}
                    className={`
                      px-4 py-2 text-sm font-mono border border-terminal-border
                      transition-colors whitespace-nowrap relative
                      ${isActive
                        ? 'bg-terminal-bg-lighter border-terminal-orange text-terminal-orange z-10'
                        : 'bg-terminal-bg text-terminal-gray hover:text-terminal-orange hover:border-terminal-orange/50'
                      }
                    `}
                    style={{
                      marginLeft: index > 0 ? '-1px' : '0',
                    }}
                  >
                    <div className="flex items-center gap-2">
                      <span>{portfolio.name}</span>
                      {isPublished && (
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                      )}
                    </div>
                  </button>

                  {/* Cover the orange line under the active tab */}
                  {isActive && hasActiveTab && (
                    <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-terminal-bg-lighter z-30"></div>
                  )}
                </div>
              );
            })}

            {/* Orange underline that spans all tabs when one is active */}
            {hasActiveTab && (
              <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-terminal-orange z-20"></div>
            )}
          </div>

          {/* Add Portfolio Button */}
          <button
            onClick={canAddProfile ? onAddPortfolio : onUpgradeClick}
            className={`ml-2 px-3 py-2 border text-sm transition-colors flex items-center gap-2 whitespace-nowrap ${canAddProfile
                ? 'bg-terminal-bg-lighter border-terminal-border hover:border-terminal-orange text-terminal-orange'
                : 'bg-terminal-bg-lighter border-terminal-border text-terminal-orange cursor-pointer hover:border-terminal-orange opacity-70 hover:opacity-100'
              }`}
            title={!canAddProfile ? 'Portfolio limit reached. Click to upgrade to Pro for unlimited portfolios.' : ''}
          >
            {canAddProfile ? <Plus size={14} /> : <Sparkles size={14} className="animate-pulse" />}
            Add
          </button>

          {/* Manage Portfolios Button */}
          {onManagePortfolios && (
            <button
              onClick={onManagePortfolios}
              className="ml-2 px-3 py-2 bg-terminal-bg-lighter border border-terminal-border hover:border-terminal-orange text-terminal-orange text-sm transition-colors flex items-center gap-2 whitespace-nowrap"
            >
              Manage Portfolios
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PortfolioTabs;

