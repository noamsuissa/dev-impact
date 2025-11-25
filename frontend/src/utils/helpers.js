// Utility function to repeat a character
export const repeat = (char, times) => char.repeat(Math.max(0, times));

// Utility function to pad a line for terminal display
export const padLine = (text, maxWidth) => {
  const textStr = text.toString();
  return `│ ${textStr}${repeat(' ', maxWidth - textStr.length - 1)}│`;
};

// Utility function to center text within a given width
export const centerText = (text, width) => {
  const padding = Math.max(0, width - text.length);
  const leftPad = Math.floor(padding / 2);
  const rightPad = padding - leftPad;
  return repeat(' ', leftPad) + text + repeat(' ', rightPad);
};

