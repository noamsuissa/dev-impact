import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';

const ProjectForm = ({ initialData, onSave, onCancel, isEditing, profiles = [], selectedProfileId }) => {
  const [company, setCompany] = useState(initialData?.company || '');
  const [projectName, setProjectName] = useState(initialData?.projectName || '');
  const [role, setRole] = useState(initialData?.role || '');
  const [teamSize, setTeamSize] = useState(initialData?.teamSize || '');
  const [problem, setProblem] = useState(initialData?.problem || '');
  const [contributions, setContributions] = useState(initialData?.contributions || ['']);
  const [metrics, setMetrics] = useState(initialData?.metrics || []);
  const [techStack, setTechStack] = useState(initialData?.techStack || []);
  const [newTech, setNewTech] = useState('');
  // Initialize profileId from initialData, selectedProfileId, or first profile
  const [profileId, setProfileId] = useState(() => {
    if (initialData?.profile_id) return initialData.profile_id;
    if (selectedProfileId) return selectedProfileId;
    if (profiles.length > 0) return profiles[0].id;
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
    setMetrics([...metrics, { primary: '', label: '', detail: '' }]);
  };

  const updateMetric = (index, field, value) => {
    const updated = [...metrics];
    updated[index][field] = value;
    setMetrics(updated);
  };

  const removeMetric = (index) => {
    setMetrics(metrics.filter((_, i) => i !== index));
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
    const project = {
      id: initialData?.id || Date.now().toString(),
      company,
      projectName,
      role,
      teamSize: parseInt(teamSize) || 1,
      problem,
      contributions: contributions.filter(c => c.trim()),
      metrics: metrics.filter(m => m.primary && m.label),
      techStack,
      profile_id: profileId
    };
    onSave(project);
  };

  const isValid = company && projectName && role && teamSize && problem && 
                  contributions.some(c => c.trim()) && techStack.length > 0 &&
                  (profileId || profiles.length === 0); // Profile is required if profiles exist

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
          &gt; Profile: {!profileId && profiles.length > 0 && <span className="text-red-400 text-xs">(Required)</span>}
        </div>
        {profiles.length > 0 ? (
          <select
            value={profileId || ''}
            onChange={(e) => setProfileId(e.target.value || null)}
            className="w-full bg-terminal-bg-lighter border border-terminal-border px-3 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange"
          >
            <option value="">-- Select Profile --</option>
            {profiles.map(profile => (
              <option key={profile.id} value={profile.id}>
                {profile.name}
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
        {metrics.map((metric, i) => (
          <div key={i} className="border border-terminal-border p-4 mb-2.5 bg-terminal-bg-lighter">
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
                value={metric.detail} 
                onChange={(val) => updateMetric(i, 'detail', val)} 
                placeholder="5min→2sec" 
              />
            </div>
            <TerminalButton onClick={() => removeMetric(i)}>
              [Remove Metric]
            </TerminalButton>
          </div>
        ))}
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

const ProjectBuilder = ({ onSave, projects = [], profiles = [], selectedProfileId }) => {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const isEditing = projectId && projectId !== 'new';
  
  // Ensure profiles is an array
  const profilesList = Array.isArray(profiles) ? profiles : [];
  
  // Debug: log profiles to see if they're being passed
  console.log('ProjectBuilder - profiles:', profilesList, 'selectedProfileId:', selectedProfileId);
  
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
      profiles={profilesList}
      selectedProfileId={selectedProfileId}
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
