/**
 * Metric Utility Functions
 * Helper functions for standardized project metrics
 */

/**
 * Check if a metric is in legacy format
 * @param {Object} metric - The metric object
 * @returns {boolean} - True if legacy format
 */
export const isLegacyMetric = (metric) => {
  return metric && typeof metric === 'object' && 
         'primary' in metric && 
         'label' in metric && 
         typeof metric.primary === 'string';
};

/**
 * Check if a metric is in standardized format
 * @param {Object} metric - The metric object
 * @returns {boolean} - True if standardized format
 */
export const isStandardizedMetric = (metric) => {
  return metric && typeof metric === 'object' && 
         'type' in metric && 
         'primary' in metric && 
         typeof metric.primary === 'object';
};

/**
 * Convert time units to seconds for calculation
 * @param {number} value - The time value
 * @param {string} unit - The unit (ms, s, min, hrs)
 * @returns {number} - Value in seconds
 */
export const convertToSeconds = (value, unit) => {
  const conversions = {
    'ms': 0.001,
    's': 1,
    'min': 60,
    'hrs': 3600
  };
  return value * (conversions[unit] || 1);
};

/**
 * Convert units to a common base for calculation
 * @param {number} value - The value to convert
 * @param {string} fromUnit - Source unit
 * @param {string} toUnit - Target unit
 * @returns {number} - Converted value
 */
export const convertUnits = (value, fromUnit, toUnit) => {
  // Time conversions
  const timeUnits = ['ms', 's', 'min', 'hrs'];
  if (timeUnits.includes(fromUnit) && timeUnits.includes(toUnit)) {
    const inSeconds = convertToSeconds(value, fromUnit);
    const conversions = {
      'ms': 1000,
      's': 1,
      'min': 1/60,
      'hrs': 1/3600
    };
    return inSeconds * conversions[toUnit];
  }
  
  // Data size conversions
  const sizeUnits = ['MB', 'GB'];
  if (sizeUnits.includes(fromUnit) && sizeUnits.includes(toUnit)) {
    if (fromUnit === 'MB' && toUnit === 'GB') return value / 1024;
    if (fromUnit === 'GB' && toUnit === 'MB') return value * 1024;
  }
  
  // No conversion needed
  return value;
};

/**
 * Calculate improvement percentage from before/after values
 * @param {Object} before - Before value object {value, unit}
 * @param {Object} after - After value object {value, unit}
 * @returns {number|null} - Improvement percentage (positive = improvement)
 */
export const calculateImprovement = (before, after) => {
  if (!before || !after) return null;
  
  try {
    const beforeValue = before.value;
    const afterValue = after.value;
    
    // Convert units if different
    let normalizedAfter = afterValue;
    if (before.unit !== after.unit) {
      normalizedAfter = convertUnits(afterValue, after.unit, before.unit);
    }
    
    // Calculate percentage change
    // For metrics where lower is better (like time), we invert the calculation
    const lowerIsBetter = ['ms', 's', 'min', 'hrs', '$'].includes(before.unit);
    
    if (lowerIsBetter) {
      // Reduction is improvement
      const reduction = ((beforeValue - normalizedAfter) / beforeValue) * 100;
      return Math.round(reduction * 10) / 10; // Round to 1 decimal
    } else {
      // Increase is improvement
      const increase = ((normalizedAfter - beforeValue) / beforeValue) * 100;
      return Math.round(increase * 10) / 10; // Round to 1 decimal
    }
  } catch (error) {
    console.error('Error calculating improvement:', error);
    return null;
  }
};

/**
 * Format a metric value with its unit
 * @param {number} value - The numeric value
 * @param {string} unit - The unit
 * @returns {string} - Formatted string
 */
export const formatMetricValue = (value, unit) => {
  // Format large numbers with commas
  const formattedValue = typeof value === 'number' 
    ? value.toLocaleString('en-US', { maximumFractionDigits: 2 })
    : value;
  
  // Unit display mapping
  const unitDisplay = {
    '%': '%',
    'x': 'x',
    '$': '$',
    'users': ' users',
    'hrs': ' hrs',
    'ms': 'ms',
    's': 's',
    'min': ' min',
    'requests': ' requests',
    'MB': ' MB',
    'GB': ' GB',
    'items': ' items',
    'calls': ' calls'
  };
  
  const displayUnit = unitDisplay[unit] || ` ${unit}`;
  
  // For currency and percentage, put symbol before/after appropriately
  if (unit === '$') {
    return `$${formattedValue}`;
  } else if (unit === '%') {
    return `${formattedValue}%`;
  } else if (unit === 'x') {
    return `${formattedValue}x`;
  } else {
    return `${formattedValue}${displayUnit}`;
  }
};

/**
 * Get color class for metric type badge
 * @param {string} type - Metric type (performance, scale, business, quality, time)
 * @returns {string} - Tailwind color class
 */
export const getMetricTypeColor = (type) => {
  const colors = {
    'performance': 'text-blue-400',
    'scale': 'text-green-400',
    'business': 'text-orange-400',
    'quality': 'text-purple-400',
    'time': 'text-yellow-400'
  };
  return colors[type] || 'text-terminal-gray';
};

/**
 * Get short display name for metric type
 * @param {string} type - Metric type
 * @returns {string} - Short display name
 */
export const getMetricTypeLabel = (type) => {
  const labels = {
    'performance': 'PERF',
    'scale': 'SCALE',
    'business': 'BIZ',
    'quality': 'QLTY',
    'time': 'TIME'
  };
  return labels[type] || type.toUpperCase();
};

/**
 * Format comparison string (before → after)
 * @param {Object} comparison - Comparison object with before and after
 * @returns {string} - Formatted comparison string
 */
export const formatComparison = (comparison) => {
  if (!comparison || !comparison.before || !comparison.after) return '';
  
  const beforeStr = formatMetricValue(comparison.before.value, comparison.before.unit);
  const afterStr = formatMetricValue(comparison.after.value, comparison.after.unit);
  
  return `${beforeStr} → ${afterStr}`;
};

/**
 * Best-effort conversion from legacy metric to standardized format
 * @param {Object} legacy - Legacy metric object
 * @returns {Object|null} - Standardized metric object or null if conversion fails
 */
export const upgradeLegacyMetric = (legacy) => {
  if (!isLegacyMetric(legacy)) return null;
  
  try {
    // Try to parse the primary value
    // Formats: "96%", "5min→2sec", "200 users", "$50K"
    const primaryStr = legacy.primary.trim();
    
    // Simple pattern matching for value and unit
    const percentMatch = primaryStr.match(/^(\d+(?:\.\d+)?)%$/);
    const timeMatch = primaryStr.match(/^(\d+(?:\.\d+)?)(ms|s|min|hrs)$/);
    const moneyMatch = primaryStr.match(/^\$(\d+(?:\.\d+)?)(K|M)?$/);
    const multipleMatch = primaryStr.match(/^(\d+(?:\.\d+)?)x$/);
    
    let value, unit;
    
    if (percentMatch) {
      value = parseFloat(percentMatch[1]);
      unit = '%';
    } else if (timeMatch) {
      value = parseFloat(timeMatch[1]);
      unit = timeMatch[2];
    } else if (moneyMatch) {
      value = parseFloat(moneyMatch[1]);
      if (moneyMatch[2] === 'K') value *= 1000;
      if (moneyMatch[2] === 'M') value *= 1000000;
      unit = '$';
    } else if (multipleMatch) {
      value = parseFloat(multipleMatch[1]);
      unit = 'x';
    } else {
      // Default fallback - treat as plain text
      return null;
    }
    
    // Guess type based on label and unit
    let type = 'performance'; // default
    const labelLower = legacy.label.toLowerCase();
    
    if (labelLower.includes('user') || labelLower.includes('scale')) {
      type = 'scale';
    } else if (labelLower.includes('cost') || labelLower.includes('revenue') || labelLower.includes('$')) {
      type = 'business';
    } else if (labelLower.includes('quality') || labelLower.includes('uptime') || labelLower.includes('error')) {
      type = 'quality';
    } else if (labelLower.includes('time') || labelLower.includes('fast') || timeMatch) {
      type = 'time';
    }
    
    return {
      type,
      primary: {
        value,
        unit,
        label: legacy.label
      },
      comparison: null,
      context: null,
      timeframe: null
    };
  } catch (error) {
    console.error('Error upgrading legacy metric:', error);
    return null;
  }
};

/**
 * Validate a standardized metric object
 * @param {Object} metric - Metric to validate
 * @returns {Object} - {valid: boolean, errors: string[]}
 */
export const validateStandardizedMetric = (metric) => {
  const errors = [];
  
  if (!metric.type || !['performance', 'scale', 'business', 'quality', 'time'].includes(metric.type)) {
    errors.push('Invalid or missing metric type');
  }
  
  if (!metric.primary || typeof metric.primary !== 'object') {
    errors.push('Primary metric value is required');
  } else {
    if (typeof metric.primary.value !== 'number') {
      errors.push('Primary value must be a number');
    }
    if (!metric.primary.unit) {
      errors.push('Primary unit is required');
    }
    if (!metric.primary.label) {
      errors.push('Primary label is required');
    }
  }
  
  if (metric.comparison) {
    if (!metric.comparison.before || !metric.comparison.after) {
      errors.push('Comparison must include both before and after values');
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
};

