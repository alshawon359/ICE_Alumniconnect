/**
 * Format a datetime string to Bangladesh timezone (Asia/Dhaka, UTC+6)
 * @param {string} dateStr - ISO datetime string from backend
 * @returns {string} Formatted date/time in Bangladesh timezone
 */
export const formatDateTimeInBDT = (dateStr) => {
  if (!dateStr) return '—';
  
  try {
    // Parse the date string
    const date = new Date(dateStr);
    
    // Format using Bangladesh timezone (Asia/Dhaka)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: 'Asia/Dhaka',
    }).format(date);
  } catch (error) {
    return '—';
  }
};

/**
 * Format a date string to Bangladesh timezone
 * @param {string} dateStr - ISO date string from backend
 * @returns {string} Formatted date in Bangladesh timezone
 */
export const formatDateInBDT = (dateStr) => {
  if (!dateStr) return '—';
  
  try {
    const date = new Date(dateStr);
    
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      timeZone: 'Asia/Dhaka',
    }).format(date);
  } catch (error) {
    return '—';
  }
};
