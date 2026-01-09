import React, { useState, useEffect, useRef } from 'react';
import { searchLocation, formatLocation } from '../../utils/photonApi';

const LocationAutocomplete = ({
  value = null, // { city, country } object or null
  onChange,
  placeholder = 'Search for a city...',
  disabled = false,
  autoFocus = false,
  className = ''
}) => {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const containerRef = useRef(null);
  const inputRef = useRef(null);
  const debounceTimerRef = useRef(null);

  // Initialize input value from prop value
  useEffect(() => {
    if (value) {
      setInputValue(formatLocation(value));
    } else {
      setInputValue('');
    }
  }, [value]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setShowSuggestions(false);
        setSelectedIndex(-1);
      }
    };

    if (showSuggestions) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showSuggestions]);

  // Debounced search function
  const performSearch = async (query) => {
    if (!query || query.trim().length < 2) {
      setSuggestions([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    try {
      const results = await searchLocation(query, { limit: 5 });
      setSuggestions(results);
      setShowSuggestions(true);
      setSelectedIndex(-1);
    } catch (error) {
      console.error('Error searching locations:', error);
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle input change with debouncing
  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    setShowSuggestions(false);
    setSelectedIndex(-1);

    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // If input is cleared, clear the selection
    if (!newValue.trim()) {
      onChange(null);
      setSuggestions([]);
      return;
    }

    // Debounce API call
    debounceTimerRef.current = setTimeout(() => {
      performSearch(newValue);
    }, 300);
  };

  // Handle suggestion selection
  const handleSelectSuggestion = (location) => {
    setInputValue(formatLocation(location));
    setShowSuggestions(false);
    setSelectedIndex(-1);
    onChange(location);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === 'ArrowDown' && inputValue.trim().length >= 2) {
        // Trigger search if not already showing suggestions
        performSearch(inputValue);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelectSuggestion(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
      default:
        break;
    }
  };

  // Handle input focus
  const handleFocus = () => {
    if (suggestions.length > 0) {
      setShowSuggestions(true);
    } else if (inputValue.trim().length >= 2) {
      performSearch(inputValue);
    }
  };

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      <input
        ref={inputRef}
        type="text"
        className="terminal-input"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={handleFocus}
        placeholder={placeholder}
        disabled={disabled}
        autoFocus={autoFocus}
      />

      {/* Loading indicator */}
      {isLoading && (
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-terminal-gray text-sm">
          Searching...
        </div>
      )}

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-terminal-bg-lighter border border-terminal-orange max-h-60 overflow-y-auto">
          {suggestions.map((location, index) => {
            const formatted = formatLocation(location);
            return (
              <button
                key={`${location.city || ''}-${location.country || ''}-${index}`}
                type="button"
                onClick={() => handleSelectSuggestion(location)}
                className={`w-full px-3 py-2 text-left font-mono text-sm transition-colors ${
                  index === selectedIndex
                    ? 'bg-terminal-orange/20 text-terminal-orange'
                    : 'text-terminal-text hover:bg-terminal-orange/10 hover:text-terminal-orange'
                }`}
              >
                {formatted}
              </button>
            );
          })}
        </div>
      )}

      {/* No results message */}
      {showSuggestions && !isLoading && suggestions.length === 0 && inputValue.trim().length >= 2 && (
        <div className="absolute z-10 w-full mt-1 bg-terminal-bg-lighter border border-terminal-border p-3 text-terminal-gray text-sm">
          No locations found
        </div>
      )}
    </div>
  );
};

export default LocationAutocomplete;
