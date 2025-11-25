import React from 'react';

const TerminalInput = ({ value, onChange, placeholder, className = '' }) => (
  <input
    className={`terminal-input ${className}`}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
  />
);

export default TerminalInput;

