import { useEffect } from 'react';

/**
 * Hook to inject and manage JSON-LD structured data for SEO
 * @param {Object} structuredData - The structured data object to inject as JSON-LD
 * @param {string} id - Optional unique ID for the script tag (for cleanup)
 */
export const useStructuredData = (structuredData, id = 'structured-data') => {
  useEffect(() => {
    if (!structuredData) return;

    // Remove existing script with same ID if it exists
    const existingScript = document.getElementById(id);
    if (existingScript) {
      existingScript.remove();
    }

    // Create new script element
    const script = document.createElement('script');
    script.id = id;
    script.type = 'application/ld+json';
    script.text = JSON.stringify(structuredData);
    document.head.appendChild(script);

    // Cleanup function
    return () => {
      const scriptToRemove = document.getElementById(id);
      if (scriptToRemove) {
        document.head.removeChild(scriptToRemove);
      }
    };
  }, [structuredData, id]);
};
