import React from 'react';

const TerminalInput = ({ 
  value, 
  onChange, 
  placeholder, 
  type = 'text',
  disabled = false,
  required = false,
  className = '' 
}) => (
  <input
    type={type}
    className={`terminal-input ${className}`}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
    disabled={disabled}
    required={required}
  />
);

export default TerminalInput;

