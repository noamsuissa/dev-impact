import React from 'react';
import TerminalButton from './common/TerminalButton';
import { repeat, padLine, centerText, wrapText } from '../utils/helpers';
import {
  isLegacyMetric,
  formatMetricValue,
  formatComparison,
  getMetricTypeLabel,
  getMetricTypeColor
} from '../utils/metrics';

const ProjectCard = ({ project, onEdit, onDelete, onClick, compact = false }) => {
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
    const wrappedCentered = (text, className, shouldColorText = false) => {
      const wrapped = wrapText(text, cardWidth);
      return wrapped.map(line => {
        const centeredLine = centerText(line, cardWidth);
        return {
          text: '│' + centeredLine + '│',
          className,
          // Store the centered line (with spaces) for coloring, not trimmed
          colorContent: shouldColorText ? centeredLine : undefined
        };
      });
    };

    // Check if legacy or standardized metric
    if (isLegacyMetric(metric)) {
      // Legacy format
      lines.push({ text: '┌' + repeat('─', cardWidth) + '┐' });
      wrappedCentered(metric.primary).forEach(l => lines.push(l));
      wrappedCentered(metric.label).forEach(l => lines.push(l));

      if (metric.detail) {
        lines.push({ text: '├' + repeat('─', cardWidth) + '┤' });
        wrappedCentered(metric.detail).forEach(l => lines.push(l));
      }

      lines.push({ text: '└' + repeat('─', cardWidth) + '┘' });
    } else {
      // Standardized format
      const typeColor = getMetricTypeColor(metric.type);
      const typeLabel = getMetricTypeLabel(metric.type);

      lines.push({ text: '┌' + repeat('─', cardWidth) + '┐' });

      // Type badge (color only the text, not borders)
      wrappedCentered(typeLabel, typeColor, true).forEach(l => lines.push(l));

      // Primary value
      const primaryValue = formatMetricValue(metric.primary.value, metric.primary.unit);
      wrappedCentered(primaryValue, 'font-bold').forEach(l => lines.push(l));

      // Label
      wrappedCentered(metric.primary.label).forEach(l => lines.push(l));

      // Comparison if present
      if (metric.comparison) {
        lines.push({ text: '├' + repeat('─', cardWidth) + '┤' });
        const comparisonStr = formatComparison(metric.comparison);
        wrappedCentered(comparisonStr, 'text-xs').forEach(l => lines.push(l));
      }

      // Context/Timeframe if present
      if (metric.context?.scope || metric.context?.frequency || metric.timeframe) {
        if (!metric.comparison) {
          lines.push({ text: '├' + repeat('─', cardWidth) + '┤' });
        }
        if (metric.context?.scope) {
          wrappedCentered(metric.context.scope, 'text-xs').forEach(l => lines.push(l));
        }
        if (metric.context?.frequency) {
          wrappedCentered(metric.context.frequency, 'text-xs').forEach(l => lines.push(l));
        }
        if (metric.timeframe) {
          wrappedCentered(metric.timeframe, 'text-xs').forEach(l => lines.push(l));
        }
      }

      lines.push({ text: '└' + repeat('─', cardWidth) + '┘' });
    }

    return lines;
  };

  const metricCards = project.metrics.map(m => buildMetricCard(m));
  const maxMetricLines = Math.max(...metricCards.map(c => c.length), 0);

  // Calculate how many metrics fit per line
  const metricSpacing = compact ? 14 : 18; // card width + 2 for padding
  const metricsPerLine = Math.floor((maxWidth - 4) / metricSpacing); // -4 for borders and padding

  // Group metrics into rows that fit within maxWidth
  const metricRows = [];
  for (let i = 0; i < metricCards.length; i += metricsPerLine) {
    metricRows.push(metricCards.slice(i, i + metricsPerLine));
  }

  // Build combined metrics with wrapping
  const combinedMetrics = [];
  metricRows.forEach((row) => {
    for (let i = 0; i < maxMetricLines; i++) {
      let line = '│ ';
      const colorSegments = []; // Track all colored segments on this line

      row.forEach((card, idx) => {
        const lineObj = card[i] || { text: repeat(' ', metricSpacing), className: '' };
        const currentPos = line.length; // Position where this card's text starts
        line += lineObj.text || repeat(' ', metricSpacing);

        // Track this colored segment if it exists
        if (lineObj.className && lineObj.colorContent) {
          colorSegments.push({
            className: lineObj.className,
            content: lineObj.colorContent,
            startPos: currentPos
          });
        }

        if (idx < row.length - 1) line += '  ';
      });
      const currentLength = line.length - 2;
      line += repeat(' ', maxWidth - currentLength - 1) + '│';
      combinedMetrics.push({ text: line, colorSegments });
    }
  });

  // Helper to render line with highlighted label
  const renderLineWithLabel = (label, content, maxWidth) => {
    const fullText = `${label} ${content}`;
    const padded = padLine(fullText, maxWidth);
    const labelIndex = padded.indexOf(label);
    if (labelIndex !== -1) {
      const beforeLabel = padded.substring(0, labelIndex);
      const afterLabel = padded.substring(labelIndex + label.length);
      return (
        <>
          {beforeLabel}
          <span className="text-terminal-orange inline">{label}</span>
          {afterLabel}
        </>
      );
    }
    return padded;
  };

  // Helper to render multiline with highlighted label (first line only)
  const renderMultiLineWithLabel = (label, content, maxWidth) => {
    const wrapped = wrapText(`${label} ${content}`, maxWidth - 2);
    return wrapped.map((line, idx) => {
      const padded = padLine(line, maxWidth);
      if (idx === 0 && line.includes(label)) {
        const labelIndex = padded.indexOf(label);
        if (labelIndex !== -1) {
          const beforeLabel = padded.substring(0, labelIndex);
          const afterLabel = padded.substring(labelIndex + label.length);
          return (
            <React.Fragment key={idx}>
              {beforeLabel}
              <span className="text-terminal-orange inline">{label}</span>
              {afterLabel}
            </React.Fragment>
          );
        }
      }
      return <React.Fragment key={idx}>{padded}</React.Fragment>;
    });
  };

  return (
    <div
      className={`font-mono ${compact ? 'text-xs' : 'text-sm'} leading-normal text-terminal-text whitespace-pre overflow-x-auto flex flex-col h-full ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick ? () => onClick(project) : undefined}
    >
      <div className="inline-block min-w-fit flex-grow">
      <div>┌{repeat('─', maxWidth)}┐</div>
      <div>{renderLineWithLabel('Company:', project.company, maxWidth)}</div>
      {padMultiLine(project.projectName, maxWidth).map((line, idx) => (
        <div key={idx}>{line}</div>
      ))}
      <div>{padLineLocal(`${project.role} • Team of ${project.teamSize}`)}</div>
      <div>├{repeat('─', maxWidth)}┤</div>
      <div>{padLineLocal('')}</div>
      {renderMultiLineWithLabel('Problem:', project.problem, maxWidth).map((line, idx) => (
        <div key={`prob-${idx}`}>{line}</div>
      ))}
      <div>{padLineLocal('')}</div>
      <div>{renderLineWithLabel('Solution:', '', maxWidth)}</div>
      {project.contributions.map((contrib, idx) =>
        padMultiLine(`• ${contrib}`, maxWidth).map((line, lineIdx) => (
          <div key={`${idx}-${lineIdx}`}>{line}</div>
        ))
      )}
      <div>{padLineLocal('')}</div>

      {combinedMetrics.map((lineObj, idx) => {
        // Apply multiple colored segments if present
        if (lineObj.colorSegments && lineObj.colorSegments.length > 0) {
          const text = lineObj.text;
          const parts = [];
          let lastIndex = 0;

          // Process each colored segment
          lineObj.colorSegments.forEach((segment, segIdx) => {
            const contentIndex = text.indexOf(segment.content, segment.startPos);
            if (contentIndex !== -1) {
              // Add text before this colored segment
              if (contentIndex > lastIndex) {
                parts.push(
                  <span key={`text-${segIdx}`}>
                    {text.substring(lastIndex, contentIndex)}
                  </span>
                );
              }
              // Add the colored segment
              parts.push(
                <span key={`color-${segIdx}`} className={segment.className}>
                  {text.substring(contentIndex, contentIndex + segment.content.length)}
                </span>
              );
              lastIndex = contentIndex + segment.content.length;
            }
          });

          // Add any remaining text after the last colored segment
          if (lastIndex < text.length) {
            parts.push(
              <span key="text-end">{text.substring(lastIndex)}</span>
            );
          }

          return <div key={idx}>{parts}</div>;
        }
        return <div key={idx}>{lineObj.text}</div>;
      })}

      <div>{padLineLocal('')}</div>
      {padMultiLine(project.techStack.join(' • '), maxWidth).map((line, idx) => (
        <div key={`tech-${idx}`}>{line}</div>
      ))}
      <div>└{repeat('─', maxWidth)}┘</div>
      </div>

      {(onEdit || onDelete) && (
        <div className="mt-2.5 ml-[4px] flex gap-2.5">
          {onEdit && (
            <TerminalButton onClick={(e) => {
              e.stopPropagation(); // Prevent modal from opening
              onEdit(project);
            }}>
              [Edit]
            </TerminalButton>
          )}
          {onDelete && (
            <TerminalButton onClick={(e) => {
              e.stopPropagation(); // Prevent modal from opening
              onDelete(project.id);
            }}>
              [Delete]
            </TerminalButton>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectCard;
