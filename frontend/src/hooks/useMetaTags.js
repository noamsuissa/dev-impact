import { useEffect } from 'react';

/**
 * Hook to dynamically update meta tags for SEO and OpenGraph
 * @param {Object} metaTags - Object containing meta tag properties
 * @param {string} metaTags.title - Page title
 * @param {string} metaTags.description - Meta description
 * @param {string} metaTags.image - OG image URL
 * @param {string} metaTags.url - Canonical URL
 * @param {string} metaTags.type - OG type (default: 'website')
 */
export const useMetaTags = ({ title, description, image, url, type = 'website' }) => {
  useEffect(() => {
    // Store original values to restore on unmount
    const originalTitle = document.title;
    const originalTags = {
      description: document.querySelector('meta[name="description"]')?.content,
      ogTitle: document.querySelector('meta[property="og:title"]')?.content,
      ogDescription: document.querySelector('meta[property="og:description"]')?.content,
      ogImage: document.querySelector('meta[property="og:image"]')?.content,
      ogUrl: document.querySelector('meta[property="og:url"]')?.content,
      ogType: document.querySelector('meta[property="og:type"]')?.content,
      twitterTitle: document.querySelector('meta[name="twitter:title"]')?.content,
      twitterDescription: document.querySelector('meta[name="twitter:description"]')?.content,
      twitterImage: document.querySelector('meta[name="twitter:image"]')?.content,
      twitterUrl: document.querySelector('meta[name="twitter:url"]')?.content,
      canonical: document.querySelector('link[rel="canonical"]')?.href,
    };

    // Update title
    if (title) {
      document.title = title;
    }

    // Helper function to update or create meta tag
    const updateMetaTag = (selector, attributeName, attributeValue, value) => {
      if (!value) return;
      
      let element = document.querySelector(selector);
      if (!element) {
        element = document.createElement('meta');
        element.setAttribute(attributeName, attributeValue);
        document.head.appendChild(element);
      }
      element.setAttribute('content', value);
    };

    // Update meta description
    updateMetaTag('meta[name="description"]', 'name', 'description', description);

    // Update OpenGraph tags
    updateMetaTag('meta[property="og:title"]', 'property', 'og:title', title);
    updateMetaTag('meta[property="og:description"]', 'property', 'og:description', description);
    updateMetaTag('meta[property="og:image"]', 'property', 'og:image', image);
    updateMetaTag('meta[property="og:url"]', 'property', 'og:url', url);
    updateMetaTag('meta[property="og:type"]', 'property', 'og:type', type);

    // Update Twitter Card tags
    updateMetaTag('meta[name="twitter:title"]', 'name', 'twitter:title', title);
    updateMetaTag('meta[name="twitter:description"]', 'name', 'twitter:description', description);
    updateMetaTag('meta[name="twitter:image"]', 'name', 'twitter:image', image);
    updateMetaTag('meta[name="twitter:url"]', 'name', 'twitter:url', url);

    // Update canonical URL
    if (url) {
      let canonical = document.querySelector('link[rel="canonical"]');
      if (!canonical) {
        canonical = document.createElement('link');
        canonical.setAttribute('rel', 'canonical');
        document.head.appendChild(canonical);
      }
      canonical.setAttribute('href', url);
    }

    // Cleanup function to restore original values
    return () => {
      document.title = originalTitle;
      
      if (originalTags.description) {
        updateMetaTag('meta[name="description"]', 'name', 'description', originalTags.description);
      }
      if (originalTags.ogTitle) {
        updateMetaTag('meta[property="og:title"]', 'property', 'og:title', originalTags.ogTitle);
      }
      if (originalTags.ogDescription) {
        updateMetaTag('meta[property="og:description"]', 'property', 'og:description', originalTags.ogDescription);
      }
      if (originalTags.ogImage) {
        updateMetaTag('meta[property="og:image"]', 'property', 'og:image', originalTags.ogImage);
      }
      if (originalTags.ogUrl) {
        updateMetaTag('meta[property="og:url"]', 'property', 'og:url', originalTags.ogUrl);
      }
      if (originalTags.ogType) {
        updateMetaTag('meta[property="og:type"]', 'property', 'og:type', originalTags.ogType);
      }
      if (originalTags.twitterTitle) {
        updateMetaTag('meta[name="twitter:title"]', 'name', 'twitter:title', originalTags.twitterTitle);
      }
      if (originalTags.twitterDescription) {
        updateMetaTag('meta[name="twitter:description"]', 'name', 'twitter:description', originalTags.twitterDescription);
      }
      if (originalTags.twitterImage) {
        updateMetaTag('meta[name="twitter:image"]', 'name', 'twitter:image', originalTags.twitterImage);
      }
      if (originalTags.twitterUrl) {
        updateMetaTag('meta[name="twitter:url"]', 'name', 'twitter:url', originalTags.twitterUrl);
      }
      if (originalTags.canonical) {
        const canonical = document.querySelector('link[rel="canonical"]');
        if (canonical) {
          canonical.setAttribute('href', originalTags.canonical);
        }
      }
    };
  }, [title, description, image, url, type]);
};

