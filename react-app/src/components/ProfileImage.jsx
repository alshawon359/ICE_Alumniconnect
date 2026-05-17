/**
 * Profile Image Component - Enhanced Version
 * 
 * Features:
 * - Displays uploaded images reliably
 * - CORS support for cross-origin requests
 * - Proper error handling and logging
 * - Supports /iceaa/ subpath deployment
 * - Shows broken image feedback in development
 * 
 * Usage:
 * <ProfileImage 
 *   src={imageUrl}
 *   alt="User name"
 *   width={96}
 *   height={96}
 *   onError={() => console.log('Image failed')}
 * />
 */

import React, { useState, useCallback, useEffect } from 'react';

const ProfileImage = React.forwardRef(({
  src,
  alt = 'Profile',
  width = 96,
  height = 96,
  className = '',
  style = {},
  onClick = null,
  onLoad = null,
  onError = null,
  borderRadius = '50%',
  objectFit = 'cover',
  crossOrigin = 'anonymous',  // Enable CORS
  ...props
}, ref) => {
  // Track if image has failed to load
  const [imageFailed, setImageFailed] = useState(false);
  const [isLoading, setIsLoading] = useState(!!src);

  // Handle image load success
  const handleLoad = useCallback((e) => {
    setImageFailed(false);
    setIsLoading(false);
    if (onLoad) onLoad(e);
    
    if (process.env.NODE_ENV === 'development') {
      console.debug('[ProfileImage] ✓ Loaded:', src);
    }
  }, [onLoad, src]);

  // Handle image load failure
  const handleError = useCallback((e) => {
    setImageFailed(true);
    setIsLoading(false);
    if (onError) onError(e);
    
    console.warn('[ProfileImage] ✗ Failed to load:', src);
    console.warn('[ProfileImage] Error details:', {
      src: src,
      alt: alt,
      error: e?.message,
      timestamp: new Date().toISOString(),
    });
  }, [onError, src, alt]);

  // Reset failed state if src changes
  useEffect(() => {
    if (src) {
      setImageFailed(false);
      setIsLoading(true);
    } else {
      setImageFailed(true);
      setIsLoading(false);
    }
  }, [src]);

  // If no URL or image failed to load, render nothing
  if (!src || imageFailed) {
    return null;
  }

  // Build final styles
  const finalStyle = {
    width,
    height,
    borderRadius,
    objectFit,
    display: 'block',
    flexShrink: 0,
    opacity: isLoading ? 0.7 : 1,
    transition: 'opacity 0.3s ease-in-out',
    ...style,
  };

  // Render image with CORS support
  return (
    <img
      ref={ref}
      src={src}
      alt={alt}
      className={className}
      style={finalStyle}
      onLoad={handleLoad}
      onError={handleError}
      onClick={onClick}
      crossOrigin={crossOrigin}
      loading="lazy"
      {...props}
    />
  );
});

ProfileImage.displayName = 'ProfileImage';

export default ProfileImage;
