import React from 'react';
import TerminalButton from './common/TerminalButton';
import { repeat, padLine, centerText, wrapText } from '../utils/helpers';

const ProjectCard = ({ project, onEdit, onDelete, compact = false }) => {
  const maxWidth = compact ? 60 : 80;
  
  const padLineLocal = (text) => padLine(text, maxWidth);
  
  const padMultiLine = (text, maxWidth) => {
    const wrapped = wrapText(text, maxWidth - 2);
    return wrapped.map(line => padLine(line, maxWidth));
  };
  
  const buildMetricCard = (metric) => {
    const cardWidth = 16;
    const lines = [];
    
    lines.push('┌' + repeat('─', cardWidth) + '┐');
    lines.push('│' + centerText(metric.primary, cardWidth) + '│');
    lines.push('│' + centerText(metric.label, cardWidth) + '│');
    
    if (metric.detail) {
      lines.push('├' + repeat('─', cardWidth) + '┤');
      lines.push('│' + centerText(metric.detail, cardWidth) + '│');
    }
    
    lines.push('└' + repeat('─', cardWidth) + '┘');
    
    return lines;
  };
  
  const metricCards = project.metrics.map(m => buildMetricCard(m));
  const maxMetricLines = Math.max(...metricCards.map(c => c.length), 0);
  
  const combinedMetrics = [];
  for (let i = 0; i < maxMetricLines; i++) {
    let line = '│ ';
    metricCards.forEach((card, idx) => {
      line += (card[i] || repeat(' ', 18));
      if (idx < metricCards.length - 1) line += '  ';
    });
    const currentLength = line.length - 2;
    line += repeat(' ', maxWidth - currentLength - 1) + '│';
    combinedMetrics.push(line);
  }

  return (
    <div style={{
      fontFamily: "'JetBrains Mono', 'Courier New', monospace",
      fontSize: compact ? '12px' : '14px',
      lineHeight: '1.5',
      color: '#e8e6e3',
      backgroundColor: '#3a3a3a',
      padding: '20px',
      whiteSpace: 'pre',
      border: '1px solid #5a5a5a',
      margin: '20px 0'
    }}>
      <div>┌{repeat('─', maxWidth)}┐</div>
      <div>{padLineLocal(`Company: ${project.company}`)}</div>
      {padMultiLine(project.projectName, maxWidth).map((line, idx) => (
        <div key={idx}>{line}</div>
      ))}
      <div>{padLineLocal(`${project.role} • Team of ${project.teamSize}`)}</div>
      <div>├{repeat('─', maxWidth)}┤</div>
      <div>{padLineLocal('')}</div>
      {padMultiLine(`Problem: ${project.problem}`, maxWidth).map((line, idx) => (
        <div key={`prob-${idx}`}>{line}</div>
      ))}
      <div>{padLineLocal('')}</div>
      <div>{padLineLocal('Solution:')}</div>
      {project.contributions.map((contrib, idx) => 
        padMultiLine(`• ${contrib}`, maxWidth).map((line, lineIdx) => (
          <div key={`${idx}-${lineIdx}`}>{line}</div>
        ))
      )}
      <div>{padLineLocal('')}</div>
      
      {combinedMetrics.map((line, idx) => (
        <div key={idx}>{line}</div>
      ))}
      
      <div>{padLineLocal('')}</div>
      {padMultiLine(project.techStack.join(' • '), maxWidth).map((line, idx) => (
        <div key={`tech-${idx}`}>{line}</div>
      ))}
      <div>└{repeat('─', maxWidth)}┘</div>
      
      {(onEdit || onDelete) && (
        <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
          {onEdit && (
            <TerminalButton onClick={() => onEdit(project)}>
              [Edit]
            </TerminalButton>
          )}
          {onDelete && (
            <TerminalButton onClick={() => onDelete(project.id)}>
              [Delete]
            </TerminalButton>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectCard;

