import React from 'react';

const TerminalInput = ({
  value,
  onChange,
  placeholder,
  type = 'text',
  disabled = false,
  required = false,
  autoComplete,
  name,
  id,
  className = ''
}) => (
  <input
    type={type}
    name={name}
    id={id}
    className={`terminal-input ${className}`}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
    disabled={disabled}
    required={required}
    autoComplete={autoComplete}
  />
);

export default TerminalInput;
