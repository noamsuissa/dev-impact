import React from 'react';
import TerminalButton from './common/TerminalButton';
import { repeat, padLine, centerText, wrapText } from '../utils/helpers';

const ProjectCard = ({ project, onEdit, onDelete, compact = false }) => {
  const maxWidth = compact ? 45 : 80;
  
  const padLineLocal = (text) => padLine(text, maxWidth);
  
  const padMultiLine = (text, maxWidth) => {
    const wrapped = wrapText(text, maxWidth - 2);
    return wrapped.map(line => padLine(line, maxWidth));
  };
  
  const buildMetricCard = (metric) => {
    const cardWidth = compact ? 12 : 16;
    const lines = [];

    // Helper to wrap and center lines for terminal card
    const wrappedCentered = (text) =>
      wrapText(text, cardWidth).map(line => '│' + centerText(line, cardWidth) + '│');

    lines.push('┌' + repeat('─', cardWidth) + '┐');
    wrappedCentered(metric.primary).forEach(l => lines.push(l));
    wrappedCentered(metric.label).forEach(l => lines.push(l));

    if (metric.detail) {
      lines.push('├' + repeat('─', cardWidth) + '┤');
      wrappedCentered(metric.detail).forEach(l => lines.push(l));
    }

    lines.push('└' + repeat('─', cardWidth) + '┘');

    return lines;
  };
  
  const metricCards = project.metrics.map(m => buildMetricCard(m));
  const maxMetricLines = Math.max(...metricCards.map(c => c.length), 0);
  
  const combinedMetrics = [];
  const metricSpacing = compact ? 14 : 18; // card width + 2 for padding
  
  for (let i = 0; i < maxMetricLines; i++) {
    let line = '│ ';
    metricCards.forEach((card, idx) => {
      line += (card[i] || repeat(' ', metricSpacing));
      if (idx < metricCards.length - 1) line += '  ';
    });
    const currentLength = line.length - 2;
    line += repeat(' ', maxWidth - currentLength - 1) + '│';
    combinedMetrics.push(line);
  }

  return (
    <div className={`font-mono ${compact ? 'text-xs' : 'text-sm'} leading-normal text-terminal-text whitespace-pre overflow-x-auto flex flex-col h-full`}>
      <div className="inline-block min-w-fit flex-grow">
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
      </div>
      
      {(onEdit || onDelete) && (
        <div className="mt-2.5 ml-[4px] flex gap-2.5">
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

