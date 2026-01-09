import React from 'react';

const TerminalButton = ({ children, onClick, disabled, className = '' }) => (
  <button
    className={`terminal-button ${className}`}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>
);

export default TerminalButton;
