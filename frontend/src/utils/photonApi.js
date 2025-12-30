/**
 * Photon OSM API utility for location search
 * Documentation: https://photon.komoot.io/
 */

const PHOTON_BASE_URL = 'https://photon.komoot.io/api';

/**
 * Search for locations using Photon API
 * @param {string} query - Search query (city name, address, etc.)
 * @param {Object} options - Search options
 * @param {number} options.limit - Maximum number of results (default: 5)
 * @param {string} options.lang - Preferred language (default: 'en')
 * @param {number} options.lat - Latitude for location bias (optional)
 * @param {number} options.lon - Longitude for location bias (optional)
 * @returns {Promise<Array>} Array of location objects with city and country
 */
export async function searchLocation(query, options = {}) {
  if (!query || query.trim().length === 0) {
    return [];
  }

  const {
    limit = 5,
    lang = 'en',
    lat = null,
    lon = null,
  } = options;

  try {
    const params = new URLSearchParams({
      q: query.trim(),
      limit: limit.toString(),
      lang,
    });

    // Add location bias if provided
    if (lat !== null && lon !== null) {
      params.append('lat', lat.toString());
      params.append('lon', lon.toString());
    }

    const response = await fetch(`${PHOTON_BASE_URL}/?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`Photon API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Parse GeoJSON FeatureCollection response
    if (!data.features || !Array.isArray(data.features)) {
      return [];
    }

    // Extract and format location data
    return data.features
      .map((feature) => {
        const props = feature.properties || {};
        
        // Extract city - prefer 'city' property, fallback to 'name'
        const city = props.city || props.name || null;
        
        // Extract country
        const country = props.country || null;

        // Only return locations that have at least a city or country
        if (!city && !country) {
          return null;
        }

        return {
          city,
          country,
          // Include full properties for potential future use
          properties: props,
          // Include coordinates for potential future use
          coordinates: feature.geometry?.coordinates || null,
        };
      })
      .filter((location) => location !== null);
  } catch (error) {
    console.error('Error searching location with Photon API:', error);
    // Return empty array on error to gracefully handle failures
    return [];
  }
}

/**
 * Format location for display
 * @param {Object} location - Location object with city and country
 * @returns {string} Formatted location string (e.g., "Berlin, Germany")
 */
export function formatLocation(location) {
  if (!location) {
    return '';
  }

  const { city, country } = location;
  
  if (city && country) {
    return `${city}, ${country}`;
  } else if (city) {
    return city;
  } else if (country) {
    return country;
  }
  
  return '';
}

