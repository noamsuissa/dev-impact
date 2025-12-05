// Utility function to repeat a character
export const repeat = (char, times) => char.repeat(Math.max(0, times));

// Utility function to wrap text into multiple lines
export const wrapText = (text, maxWidth) => {
  const lines = [];
  let currentLine = '';
  const words = text.split(' ');
  
  for (const word of words) {
    // If word itself is longer than maxWidth, send word to newline
    if (word.length > maxWidth) {
      if (currentLine) {
        lines.push(currentLine);
        currentLine = '';
      }
      lines.push(word);
      continue;
    }
    if ((currentLine ? currentLine.length + 1 : 0) + word.length <= maxWidth) {
      currentLine += (currentLine ? ' ' : '') + word;
    } else {
      if (currentLine) lines.push(currentLine);
      currentLine = word;
    }
  }
  if (currentLine) lines.push(currentLine);
  
  return lines.length > 0 ? lines : [''];
};

// Utility function to pad a line for terminal display
export const padLine = (text, maxWidth) => {
  const textStr = text.toString();
  // Truncate if too long
  const truncated = textStr.length > maxWidth - 2 
    ? textStr.substring(0, maxWidth - 5) + '...' 
    : textStr;
  return `│ ${truncated}${repeat(' ', maxWidth - truncated.length - 1)}│`;
};

// Utility function to center text within a given width
export const centerText = (text, width) => {
  const truncated = text.length > width ? text.substring(0, width - 3) + '...' : text;
  const padding = Math.max(0, width - truncated.length);
  const leftPad = Math.floor(padding / 2);
  const rightPad = padding - leftPad;
  return repeat(' ', leftPad) + truncated + repeat(' ', rightPad);
};

// Utility function to check if we're on localhost
export const isLocalhost = () => {
  if (typeof window === 'undefined') return false;
  const hostname = window.location.hostname;
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname.match(/^\d+\.\d+\.\d+\.\d+$/);
};

// Utility function to generate profile URL based on environment
// On localhost: uses path-based URL (http://localhost:5173/username)
// In production: uses subdomain URL (https://username.dev-impact.io)
export const generateProfileUrl = (username) => {
  if (isLocalhost()) {
    // On localhost, use path-based URL
    const port = window.location.port || '5173';
    return `http://localhost:${port}/${username}`;
  } else {
    // In production, use subdomain URL
    const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'dev-impact.io';
    return `https://${username}.${baseDomain}`;
  }
};

