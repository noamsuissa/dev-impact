import React, { useState } from 'react';
import { ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';
import { 
  isLegacyMetric, 
  calculateImprovement
} from '../utils/metrics';

const ProjectForm = ({ initialData, onSave, onCancel, isEditing, portfolios = [], selectedPortfolioId }) => {
  const [company, setCompany] = useState(initialData?.company || '');
  const [projectName, setProjectName] = useState(initialData?.projectName || '');
  const [role, setRole] = useState(initialData?.role || '');
  const [teamSize, setTeamSize] = useState(initialData?.teamSize || '');
  const [problem, setProblem] = useState(initialData?.problem || '');
  const [contributions, setContributions] = useState(initialData?.contributions || ['']);
  const [metrics, setMetrics] = useState(() => {
    // Initialize metrics with UI flags for showing comparison/context sections
    if (initialData?.metrics) {
      return initialData.metrics.map(metric => {
        // For standardized metrics, add UI flags based on existing data
        if (metric.type) {
          return {
            ...metric,
            _showComparison: !!metric.comparison,
            _showContext: !!(metric.context || metric.timeframe)
          };
        }
        // Legacy metrics don't need these flags
        return metric;
      });
    }
    return [];
  });
  const [techStack, setTechStack] = useState(initialData?.techStack || []);
  const [newTech, setNewTech] = useState('');
  // Initialize profileId from initialData, selectedProfileId, or first profile
  const [profileId, setProfileId] = useState(() => {
    if (initialData?.portfolio_id) return initialData.portfolio_id;
    if (selectedPortfolioId) return selectedPortfolioId;
    if (portfolios.length > 0) return portfolios[0].id;
    return null;
  });

  const addContribution = () => {
    setContributions([...contributions, '']);
  };

  const updateContribution = (index, value) => {
    const updated = [...contributions];
    updated[index] = value;
    setContributions(updated);
  };

  const removeContribution = (index) => {
    setContributions(contributions.filter((_, i) => i !== index));
  };

  const addMetric = () => {
    // Add a new standardized metric by default
    setMetrics([...metrics, { 
      type: 'performance',
      primary: { value: '', unit: '%', label: '' },
      comparison: null,
      context: null,
      timeframe: null,
      _showComparison: false,
      _showContext: false
    }]);
  };

  const updateMetric = (index, field, value) => {
    const updated = [...metrics];
    
    // Handle nested updates for standardized metrics
    if (field.includes('.')) {
      const parts = field.split('.');
      let current = updated[index];
      
      // Navigate to the parent object
      for (let i = 0; i < parts.length - 1; i++) {
        if (!current[parts[i]]) {
          current[parts[i]] = {};
        }
        current = current[parts[i]];
      }
      
      // Set the final value
      current[parts[parts.length - 1]] = value;
    } else {
      updated[index][field] = value;
    }
    
    // Auto-calculate improvement if comparison is complete
    if (field.startsWith('comparison.') && updated[index].comparison) {
      const comp = updated[index].comparison;
      if (comp.before?.value !== undefined && comp.before?.unit && 
          comp.after?.value !== undefined && comp.after?.unit) {
        const improvement = calculateImprovement(comp.before, comp.after);
        if (improvement !== null && updated[index].primary) {
          // Optionally update primary value with calculated improvement
          // For now, just log it
          console.log('Calculated improvement:', improvement + '%');
        }
      }
    }
    
    setMetrics(updated);
  };

  const removeMetric = (index) => {
    setMetrics(metrics.filter((_, i) => i !== index));
  };
  
  const toggleMetricComparison = (index) => {
    const updated = [...metrics];
    const metric = updated[index];
    
    if (metric._showComparison) {
      // Hide but don't clear - just hide the UI
      metric._showComparison = false;
    } else {
      // Show and initialize if needed
      metric._showComparison = true;
      if (!metric.comparison) {
        metric.comparison = {
          before: { value: undefined, unit: metric.primary?.unit || 's' },
          after: { value: undefined, unit: metric.primary?.unit || 's' }
        };
      }
    }
    
    setMetrics(updated);
  };
  
  const toggleMetricContext = (index) => {
    const updated = [...metrics];
    const metric = updated[index];
    
    if (metric._showContext) {
      // Hide but don't clear - just hide the UI
      metric._showContext = false;
    } else {
      // Show and initialize if needed
      metric._showContext = true;
      if (!metric.context) {
        metric.context = { frequency: '', scope: '' };
      }
    }
    
    setMetrics(updated);
  };

  const addTech = () => {
    if (newTech.trim() && !techStack.includes(newTech.trim())) {
      setTechStack([...techStack, newTech.trim()]);
      setNewTech('');
    }
  };

  const removeTech = (tech) => {
    setTechStack(techStack.filter(t => t !== tech));
  };

  const handleSave = () => {
    // Clean up metrics before saving
    const cleanedMetrics = metrics
      .filter(m => {
        // For legacy: must have primary and label
        if (isLegacyMetric(m)) {
          return m.primary && m.label;
        }
        // For standardized: must have type and primary value/label
        return m.type && m.primary?.value !== '' && m.primary?.label;
      })
      .map(m => {
        // Remove UI-only fields
        const { _showComparison, _showContext, ...cleaned } = m;
        
        // Clean up null/empty optional fields
        // Check for undefined explicitly (0 is a valid value!)
        if (!cleaned.comparison || 
            cleaned.comparison.before?.value === undefined || 
            cleaned.comparison.after?.value === undefined) {
          cleaned.comparison = null;
        }
        if (!cleaned.context || (!cleaned.context.frequency && !cleaned.context.scope)) {
          cleaned.context = null;
        }
        if (!cleaned.timeframe) {
          cleaned.timeframe = null;
        }
        
        return cleaned;
      });
    
    const project = {
      id: initialData?.id || Date.now().toString(),
      company,
      projectName,
      role,
      teamSize: parseInt(teamSize) || 1,
      problem,
      contributions: contributions.filter(c => c.trim()),
      metrics: cleanedMetrics,
      techStack,
      portfolio_id: profileId
    };
    onSave(project);
  };

  const isValid = company && projectName && role && teamSize && problem &&
    contributions.some(c => c.trim()) && techStack.length > 0 &&
    (profileId || portfolios.length === 0); // Portfolio is required if portfolios exist

  return (
    <div className="p-10 max-w-[800px] mx-auto">
      <div className="mb-10 flex items-center gap-5">
        <TerminalButton onClick={onCancel}>
          <ArrowLeft size={16} className="inline mr-2" />
          [Back]
        </TerminalButton>
        <div className="text-xl">
          &gt; {isEditing ? 'Edit' : 'New'} Project
        </div>
      </div>

      <div className="mb-5">
        <div className="mb-2">
          &gt; Portfolio: {!profileId && portfolios.length > 0 && <span className="text-red-400 text-xs">(Required)</span>}
        </div>
        {portfolios.length > 0 ? (
          <select
            value={profileId || ''}
            onChange={(e) => setProfileId(e.target.value || null)}
            className="w-full bg-terminal-bg-lighter border border-terminal-border px-3 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange"
          >
            <option value="">-- Select Profile --</option>
            {portfolios.map(portfolio => (
              <option key={portfolio.id} value={portfolio.id}>
                {portfolio.name}
              </option>
            ))}
          </select>
        ) : (
          <div className="text-terminal-gray text-sm border border-terminal-border px-3 py-2 bg-terminal-bg-lighter">
            No profiles available. Create a profile first from the Dashboard.
          </div>
        )}
      </div>

      <div className="mb-5">
        <div className="mb-2">&gt; Company:</div>
        <TerminalInput value={company} onChange={setCompany} placeholder="TechCorp" />
      </div>

      <div className="mb-5">
        <div className="mb-2">&gt; Project Name:</div>
        <TerminalInput value={projectName} onChange={setProjectName} placeholder="Real-time Analytics Dashboard" />
      </div>

      <div className="grid grid-cols-2 gap-5 mb-5">
        <div>
          <div className="mb-2">&gt; Your Role:</div>
          <TerminalInput value={role} onChange={setRole} placeholder="Senior Frontend Engineer" />
        </div>
        <div>
          <div className="mb-2">&gt; Team Size:</div>
          <TerminalInput value={teamSize} onChange={setTeamSize} placeholder="5" />
        </div>
      </div>

      <div className="mb-5">
        <div className="mb-2">&gt; Problem (one line):</div>
        <TerminalInput value={problem} onChange={setProblem} placeholder="5min dashboard load blocking marketing team" />
      </div>

      <div className="mb-5">
        <div className="mb-2">&gt; Your Solution (3-5 bullets):</div>
        {contributions.map((contrib, i) => (
          <div key={i} className="mb-2.5 flex gap-2.5">
            <TerminalInput
              value={contrib}
              onChange={(val) => updateContribution(i, val)}
              placeholder="WebSocket-based real-time updates"
            />
            <TerminalButton onClick={() => removeContribution(i)}>
              [-]
            </TerminalButton>
          </div>
        ))}
        <TerminalButton onClick={addContribution}>
          [+ Add Bullet]
        </TerminalButton>
      </div>

      <div className="mb-5">
        <div className="mb-2">&gt; Impact Metrics:</div>
        {metrics.map((metric, i) => {
          const isLegacy = isLegacyMetric(metric);
          
          return (
            <div key={i} className="border border-terminal-border p-4 mb-2.5 bg-terminal-bg-lighter">
              {isLegacy ? (
                // Legacy metric form (read-only with upgrade option)
                <>
                  <div className="mb-2 text-xs text-terminal-orange">Legacy Format</div>
                  <div className="grid grid-cols-2 gap-2.5 mb-2.5">
                    <div>
                      <div className="mb-1 text-xs">Value:</div>
                      <TerminalInput
                        value={metric.primary}
                        onChange={(val) => updateMetric(i, 'primary', val)}
                        placeholder="96%"
                      />
                    </div>
                    <div>
                      <div className="mb-1 text-xs">Label:</div>
                      <TerminalInput
                        value={metric.label}
                        onChange={(val) => updateMetric(i, 'label', val)}
                        placeholder="faster"
                      />
                    </div>
                  </div>
                  <div className="mb-2.5">
                    <div className="mb-1 text-xs">Detail (optional):</div>
                    <TerminalInput
                      value={metric.detail || ''}
                      onChange={(val) => updateMetric(i, 'detail', val)}
                      placeholder="5min→2sec"
                    />
                  </div>
                </>
              ) : (
                // Standardized metric form
                <>
                  {/* Type Selector */}
                  <div className="mb-2.5">
                    <div className="mb-1 text-xs">Type:</div>
                    <select
                      value={metric.type || 'performance'}
                      onChange={(e) => updateMetric(i, 'type', e.target.value)}
                      className="w-full bg-terminal-bg-lighter border border-terminal-border px-3 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange"
                    >
                      <option value="performance">Performance</option>
                      <option value="scale">Scale</option>
                      <option value="business">Business</option>
                      <option value="quality">Quality</option>
                      <option value="time">Time</option>
                    </select>
                  </div>
                  
                  {/* Primary Value */}
                  <div className="mb-2.5">
                    <div className="mb-1 text-xs">Primary Metric:</div>
                    <div className="grid grid-cols-3 gap-2.5">
                      <div>
                        <div className="mb-1 text-xs">Value:</div>
                        <TerminalInput
                          type="number"
                          value={metric.primary?.value === undefined || metric.primary?.value === '' ? '' : metric.primary.value}
                          onChange={(val) => {
                            if (val === '') {
                              updateMetric(i, 'primary.value', '');
                            } else {
                              const numVal = parseFloat(val);
                              if (!isNaN(numVal)) {
                                updateMetric(i, 'primary.value', numVal);
                              }
                            }
                          }}
                          placeholder="96"
                        />
                      </div>
                      <div>
                        <div className="mb-1 text-xs">Unit:</div>
                        <select
                          value={metric.primary?.unit || '%'}
                          onChange={(e) => updateMetric(i, 'primary.unit', e.target.value)}
                          className="w-full bg-terminal-bg-lighter border border-terminal-border px-3 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange text-sm"
                        >
                          <option value="%">%</option>
                          <option value="x">x</option>
                          <option value="$">$</option>
                          <option value="users">users</option>
                          <option value="hrs">hrs</option>
                          <option value="ms">ms</option>
                          <option value="s">s</option>
                          <option value="min">min</option>
                          <option value="requests">requests</option>
                          <option value="MB">MB</option>
                          <option value="GB">GB</option>
                          <option value="items">items</option>
                          <option value="calls">calls</option>
                        </select>
                      </div>
                      <div>
                        <div className="mb-1 text-xs">Label:</div>
                        <TerminalInput
                          value={metric.primary?.label || ''}
                          onChange={(val) => updateMetric(i, 'primary.label', val)}
                          placeholder="faster"
                        />
                      </div>
                    </div>
                  </div>
                  
                  {/* Comparison Section (Collapsible) */}
                  <div className="mb-2.5">
                    <button
                      type="button"
                      onClick={() => toggleMetricComparison(i)}
                      className="flex items-center gap-2 text-sm text-terminal-orange hover:underline mb-2"
                    >
                      {metric._showComparison ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      {metric._showComparison ? 'Hide' : 'Add'} Before/After Comparison
                    </button>
                    
                    {metric._showComparison && (
                      <div className="border border-terminal-border p-3 bg-terminal-bg">
                        <div className="grid grid-cols-2 gap-2.5">
                          <div>
                            <div className="mb-1 text-xs">Before:</div>
                            <div className="flex gap-2">
                              <TerminalInput
                                type="number"
                                value={metric.comparison?.before?.value === undefined ? '' : metric.comparison.before.value}
                                onChange={(val) => {
                                  if (val === '') {
                                    updateMetric(i, 'comparison.before.value', undefined);
                                  } else {
                                    const numVal = parseFloat(val);
                                    if (!isNaN(numVal)) {
                                      updateMetric(i, 'comparison.before.value', numVal);
                                    }
                                  }
                                }}
                                placeholder="5"
                                className="flex-1"
                              />
                              <select
                                value={metric.comparison?.before?.unit || 'min'}
                                onChange={(e) => {
                                  const newUnit = e.target.value;
                                  updateMetric(i, 'comparison.before.unit', newUnit);
                                  // Sync the after unit to match
                                  updateMetric(i, 'comparison.after.unit', newUnit);
                                }}
                                className="w-24 bg-terminal-bg-lighter border border-terminal-border px-2 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange text-sm"
                              >
                                <option value="%">%</option>
                                <option value="x">x</option>
                                <option value="$">$</option>
                                <option value="ms">ms</option>
                                <option value="s">s</option>
                                <option value="min">min</option>
                                <option value="hrs">hrs</option>
                                <option value="users">users</option>
                                <option value="requests">req</option>
                                <option value="items">items</option>
                                <option value="calls">calls</option>
                                <option value="MB">MB</option>
                                <option value="GB">GB</option>
                              </select>
                            </div>
                          </div>
                          <div>
                            <div className="mb-1 text-xs">After:</div>
                            <div className="flex gap-2">
                              <TerminalInput
                                type="number"
                                value={metric.comparison?.after?.value === undefined ? '' : metric.comparison.after.value}
                                onChange={(val) => {
                                  if (val === '') {
                                    updateMetric(i, 'comparison.after.value', undefined);
                                  } else {
                                    const numVal = parseFloat(val);
                                    if (!isNaN(numVal)) {
                                      updateMetric(i, 'comparison.after.value', numVal);
                                    }
                                  }
                                }}
                                placeholder="2"
                                className="flex-1"
                              />
                              <select
                                value={metric.comparison?.after?.unit || 's'}
                                onChange={(e) => {
                                  const newUnit = e.target.value;
                                  updateMetric(i, 'comparison.after.unit', newUnit);
                                  // Sync the before unit to match
                                  updateMetric(i, 'comparison.before.unit', newUnit);
                                }}
                                className="w-24 bg-terminal-bg-lighter border border-terminal-border px-2 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange text-sm"
                              >
                                <option value="%">%</option>
                                <option value="x">x</option>
                                <option value="$">$</option>
                                <option value="ms">ms</option>
                                <option value="s">s</option>
                                <option value="min">min</option>
                                <option value="hrs">hrs</option>
                                <option value="users">users</option>
                                <option value="requests">req</option>
                                <option value="items">items</option>
                                <option value="calls">calls</option>
                                <option value="MB">MB</option>
                                <option value="GB">GB</option>
                              </select>
                            </div>
                          </div>
                        </div>
                        {metric.comparison?.before?.value !== undefined && metric.comparison?.after?.value !== undefined && (
                          <div className="mt-2 text-xs text-green-400">
                            Improvement: {calculateImprovement(metric.comparison.before, metric.comparison.after)}%
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Context Section (Collapsible) */}
                  <div className="mb-2.5">
                    <button
                      type="button"
                      onClick={() => toggleMetricContext(i)}
                      className="flex items-center gap-2 text-sm text-terminal-orange hover:underline mb-2"
                    >
                      {metric._showContext ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      {metric._showContext ? 'Hide' : 'Add'} Context & Timeframe
                    </button>
                    
                    {metric._showContext && (
                      <div className="border border-terminal-border p-3 bg-terminal-bg">
                        <div className="mb-2.5">
                          <div className="mb-1 text-xs">Frequency:</div>
                          <select
                            value={metric.context?.frequency || ''}
                            onChange={(e) => updateMetric(i, 'context.frequency', e.target.value || null)}
                            className="w-full bg-terminal-bg-lighter border border-terminal-border px-3 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange"
                          >
                            <option value="">-- Select --</option>
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                            <option value="monthly">Monthly</option>
                            <option value="annually">Annually</option>
                            <option value="one_time">One Time</option>
                          </select>
                        </div>
                        <div className="mb-2.5">
                          <div className="mb-1 text-xs">Scope:</div>
                          <TerminalInput
                            value={metric.context?.scope || ''}
                            onChange={(val) => updateMetric(i, 'context.scope', val || null)}
                            placeholder="200 daily users"
                          />
                        </div>
                        <div>
                          <div className="mb-1 text-xs">Timeframe:</div>
                          <TerminalInput
                            value={metric.timeframe || ''}
                            onChange={(val) => updateMetric(i, 'timeframe', val || null)}
                            placeholder="3 months"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
              
              <TerminalButton onClick={() => removeMetric(i)}>
                [Remove Metric]
              </TerminalButton>
            </div>
          );
        })}
        <TerminalButton onClick={addMetric}>
          [+ Add Metric]
        </TerminalButton>
      </div>

      <div className="mb-5">
        <div className="mb-2">&gt; Tech Stack:</div>
        <div className="flex flex-wrap gap-2.5 mb-2.5">
          {techStack.map(tech => (
            <div key={tech} className="border border-terminal-orange py-1 px-2.5 flex items-center gap-2 bg-terminal-bg-lighter">
              {tech}
              <button
                onClick={() => removeTech(tech)}
                className="bg-transparent border-none text-terminal-orange cursor-pointer p-0 text-xl"
              >
                ×
              </button>
            </div>
          ))}
        </div>
        <div className="flex gap-2.5">
          <TerminalInput
            value={newTech}
            onChange={setNewTech}
            placeholder="React"
          />
          <TerminalButton onClick={addTech}>
            [Add]
          </TerminalButton>
        </div>
      </div>

      <div className="flex gap-5 mt-10">
        <TerminalButton onClick={handleSave} disabled={!isValid}>
          [Save Project]
        </TerminalButton>
        <TerminalButton onClick={onCancel}>
          [Cancel]
        </TerminalButton>
      </div>
    </div>
  );
};

const ProjectBuilder = ({ onSave, projects = [], portfolios = [], selectedPortfolioId }) => {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const isEditing = projectId && projectId !== 'new';

  // Ensure profiles is an array
  const portfoliosList = Array.isArray(portfolios) ? portfolios : [];

  // Derive project from props instead of syncing to state
  const project = isEditing && projects.length > 0
    ? projects.find(p => p.id === projectId)
    : null;

  // If editing but project not found yet (and projects likely loading or empty),
  // we can show a loading state or just wait.
  const isLoading = isEditing && !project && projects.length === 0;

  // If projects have loaded but the specific project isn't found, it's a 404 case.
  const isNotFound = isEditing && !project && projects.length > 0;

  if (isLoading) {
    return (
      <div className="p-10 text-center">
        <div className="fade-in">&gt; Loading project...</div>
      </div>
    );
  }

  if (isNotFound) {
    return (
      <div className="p-10 max-w-[800px] mx-auto">
        <div className="mb-10 flex items-center gap-5">
          <TerminalButton onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={16} className="inline mr-2" />
            [Back]
          </TerminalButton>
          <div className="text-xl">
            &gt; Project Not Found
          </div>
        </div>
        <div className="border border-terminal-border p-10 text-center">
          <div className="text-terminal-orange mb-5 text-lg">
            ✗ Project with ID "{projectId}" not found
          </div>
          <div className="text-terminal-gray mb-5">
            The project you're trying to edit doesn't exist or may have been deleted.
          </div>
          <TerminalButton onClick={() => navigate('/dashboard')}>
            [Return to Dashboard]
          </TerminalButton>
        </div>
      </div>
    );
  }

  // Use key to force re-mounting when project ID changes
  return (
    <ProjectForm
      key={project?.id || 'new'}
      initialData={project}
      portfolios={portfoliosList}
      selectedPortfolioId={selectedPortfolioId}
      onSave={async (data) => {
        try {
          await onSave(data);
          navigate('/dashboard');
        } catch {
          // Error is already handled in handleSaveProject (alert shown)
          // Don't navigate on error - stay on the form so user can retry
        }
      }}
      onCancel={() => navigate('/dashboard')}
      isEditing={isEditing}
    />
  );
};

export default ProjectBuilder;
