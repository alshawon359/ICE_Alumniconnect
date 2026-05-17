/**
 * Image & Upload URL Resolution Utility
 * =====================================
 * 
 * Handles all image and file URLs with proper subpath support (/iceaa/)
 * Ensures CORS headers are set correctly
 * Provides fallbacks and error handling
 * 
 * Usage:
 * - getImageUrl(photoUrl) - Get full image URL with fallback
 * - getUploadUrl(path) - Get upload directory URL
 * - buildImageSrc(user) - Build src from user object
 */

/**
 * Get the base URL for the application
 * For /iceaa/ deployment: http://domain/iceaa
 * For root deployment: http://domain
 */
function getApplicationBaseUrl() {
  if (typeof window === 'undefined') return '/';
  
  const basePath = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');
  if (basePath && basePath !== '') {
    return `${window.location.origin}${basePath}`;
  }
  return window.location.origin;
}

/**
 * Get the uploads base URL
 * For /iceaa/ deployment: http://domain/iceaa/uploads
 * For root deployment: http://domain/uploads
 */
export function getUploadsBaseUrl() {
  const appBase = getApplicationBaseUrl();
  return `${appBase}/uploads`;
}

/**
 * Get the API base URL
 * For /iceaa/ deployment: http://domain/iceaa/api
 * For root deployment: http://domain/api
 */
export function getApiBaseUrl() {
  const appBase = getApplicationBaseUrl();
  return `${appBase}/api`;
}

/**
 * Build a complete image URL from a stored path
 * 
 * @param {string} storedPath - Path from database (e.g., "profiles/user123.jpg" or "alumni/abc.jpg")
 * @returns {string} Complete URL to serve the image
 * 
 * Examples:
 * - Input: "profiles/user123.jpg"
 *   Output: "http://csf.ru.ac.bd/iceaa/uploads/profiles/user123.jpg"
 * 
 * - Input: "uploads/profiles/user123.jpg"
 *   Output: "http://csf.ru.ac.bd/iceaa/uploads/profiles/user123.jpg" (normalized)
 */
export function getImageUrl(storedPath) {
  if (!storedPath || typeof storedPath !== 'string') {
    return null;
  }

  const path = storedPath.trim();

  // If already a full URL, return as-is
  if (/^https?:\/\//i.test(path)) {
    console.debug('[getImageUrl] Already a full URL:', path);
    return path;
  }

  // Normalize the path - remove common prefixes
  let normalized = path
    .replace(/^\/+/, '')  // Remove leading slashes
    .replace(/^(api\/)?uploads\//i, '');  // Remove uploads/ prefix

  if (!normalized) {
    console.warn('[getImageUrl] Empty path after normalization:', path);
    return null;
  }

  const uploadsBase = getUploadsBaseUrl();
  const fullUrl = `${uploadsBase}/${normalized}`;

  console.debug('[getImageUrl]', {
    input: storedPath,
    normalized,
    uploadsBase,
    output: fullUrl,
  });

  return fullUrl;
}

/**
 * Extract and build image URL from a user object
 * Looks for various image field names
 * 
 * @param {object} user - User object from API
 * @returns {string} Image URL or null if no image found
 */
export function buildImageSrcFromUser(user) {
  if (!user || typeof user !== 'object') {
    return null;
  }

  // Try to find image in various possible fields
  const imagePath = 
    user.photo_url ||
    user.photoUrl ||
    user.photo ||
    user.avatar ||
    user.image ||
    user.profile_photo ||
    null;

  if (imagePath) {
    return getImageUrl(imagePath);
  }

  return null;
}

/**
 * Get all image URLs from a user object
 * Useful for preloading or checking what images exist
 * 
 * @param {object} user - User object from API
 * @returns {object} Object with different image types
 */
export function getAllImageUrlsFromUser(user) {
  if (!user || typeof user !== 'object') {
    return {
      profile: null,
      avatar: null,
      idcard: null,
      document: null,
    };
  }

  return {
    profile: getImageUrl(user.photo_url || user.photo),
    avatar: getImageUrl(user.avatar),
    idcard: getImageUrl(user.idcard),
    document: getImageUrl(user.document_path || user.document),
  };
}

/**
 * Preload an image URL (useful for avoiding load flashes)
 * 
 * @param {string} url - Image URL to preload
 * @returns {Promise} Resolves when image loads or rejects on error
 */
export function preloadImage(url) {
  return new Promise((resolve, reject) => {
    if (!url) {
      reject(new Error('No URL provided'));
      return;
    }

    const img = new Image();
    img.crossOrigin = 'anonymous';  // For CORS
    
    img.onload = () => {
      console.debug('[preloadImage] Loaded:', url);
      resolve(img);
    };
    
    img.onerror = () => {
      console.warn('[preloadImage] Failed to load:', url);
      reject(new Error(`Failed to load image: ${url}`));
    };

    img.src = url;
  });
}

/**
 * Get CORS-safe image URL (adds corsOrigin header if needed)
 * 
 * @param {string} url - Image URL
 * @returns {string} URL ready for CORS requests
 */
export function getCorsImageUrl(url) {
  if (!url) return null;
  
  // Most modern browsers and servers handle CORS with proper headers
  // This function is here for future expansion if needed
  return url;
}

/**
 * Log image loading diagnostics (for debugging in development)
 */
export function logImageDiagnostics(user) {
  if (typeof window === 'undefined') return;

  const allUrls = getAllImageUrlsFromUser(user);
  const baseUrl = getUploadsBaseUrl();

  console.group('[IMAGE DIAGNOSTICS]');
  console.log('User:', user?.name || user?.email || 'Unknown');
  console.log('Application Base URL:', getApplicationBaseUrl());
  console.log('Uploads Base URL:', baseUrl);
  console.log('API Base URL:', getApiBaseUrl());
  console.log('All Image URLs:', allUrls);
  console.groupEnd();
}

// Export default object with all functions
export default {
  getApplicationBaseUrl,
  getUploadsBaseUrl,
  getApiBaseUrl,
  getImageUrl,
  buildImageSrcFromUser,
  getAllImageUrlsFromUser,
  preloadImage,
  getCorsImageUrl,
  logImageDiagnostics,
};
