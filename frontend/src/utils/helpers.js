// Utility function to repeat a character
export const repeat = (char, times) => char.repeat(Math.max(0, times));

// Utility function to wrap text into multiple lines
export const wrapText = (text, maxWidth) => {
  const lines = [];
  let currentLine = '';
  const words = text.split(' ');
  
  for (const word of words) {
    if ((currentLine + word).length <= maxWidth) {
      currentLine += (currentLine ? ' ' : '') + word;
    } else {
      if (currentLine) lines.push(currentLine);
      // If single word is too long, truncate it
      if (word.length > maxWidth) {
        lines.push(word.substring(0, maxWidth - 3) + '...');
      } else {
        currentLine = word;
      }
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

