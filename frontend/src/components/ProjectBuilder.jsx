import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';

const ProjectBuilder = ({ onSave, onCancel, editProject = null }) => {
  const [company, setCompany] = useState(editProject?.company || '');
  const [projectName, setProjectName] = useState(editProject?.projectName || '');
  const [role, setRole] = useState(editProject?.role || '');
  const [teamSize, setTeamSize] = useState(editProject?.teamSize || '');
  const [problem, setProblem] = useState(editProject?.problem || '');
  const [contributions, setContributions] = useState(editProject?.contributions || ['']);
  const [metrics, setMetrics] = useState(editProject?.metrics || []);
  const [techStack, setTechStack] = useState(editProject?.techStack || []);
  const [newTech, setNewTech] = useState('');

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
      id: editProject?.id || Date.now().toString(),
      company,
      projectName,
      role,
      teamSize: parseInt(teamSize) || 1,
      problem,
      contributions: contributions.filter(c => c.trim()),
      metrics: metrics.filter(m => m.primary && m.label),
      techStack
    };
    onSave(project);
  };

  const isValid = company && projectName && role && teamSize && problem && 
                  contributions.some(c => c.trim()) && techStack.length > 0;

  return (
    <div className="p-10 max-w-[800px] mx-auto">
      <div className="mb-10 flex items-center gap-5">
        <TerminalButton onClick={onCancel}>
          <ArrowLeft size={16} className="inline mr-2" />
          [Back]
        </TerminalButton>
        <div className="text-xl">
          &gt; {editProject ? 'Edit' : 'New'} Project
        </div>
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

export default ProjectBuilder;

