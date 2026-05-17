#!/bin/bash
# ============================================================================
# Image & Upload Verification Script
# ============================================================================
# Verifies that images and uploads are working correctly in production

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

log_pass() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((CHECKS_PASSED++))
}

log_fail() {
    echo -e "${RED}[✗]${NC} $1"
    ((CHECKS_FAILED++))
}

log_warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

log_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

# ============================================================================
# Checks
# ============================================================================

check_upload_folder() {
    log_header "1. Upload Folder"
    
    UPLOAD_PATH="/var/www/html/iceaa/ICE_AlumniConnect/backend/uploads"
    
    if [ ! -d "$UPLOAD_PATH" ]; then
        log_fail "Upload folder does not exist: $UPLOAD_PATH"
        return 1
    fi
    log_pass "Upload folder exists: $UPLOAD_PATH"
    
    if [ ! -w "$UPLOAD_PATH" ]; then
        log_warn "Upload folder is not writable"
    else
        log_pass "Upload folder is writable"
    fi
    
    # Check subdirectories
    for subdir in profiles documents idcards logos; do
        if [ -d "$UPLOAD_PATH/$subdir" ]; then
            log_pass "Subdirectory exists: $subdir"
        else
            log_warn "Subdirectory missing: $subdir (will be created on first upload)"
        fi
    done
}

check_backend_upload_endpoint() {
    log_header "2. Backend Upload Endpoint"
    
    # Test local endpoint
    RESPONSE=$(curl -s -I http://localhost:5000/uploads/ 2>/dev/null | head -n1 || echo "FAILED")
    
    if echo "$RESPONSE" | grep -q "200\|403\|404"; then
        log_pass "Backend upload endpoint responds: $RESPONSE"
    else
        log_fail "Backend upload endpoint not responding: $RESPONSE"
    fi
}

check_nginx_uploads_route() {
    log_header "3. Nginx Uploads Route"
    
    # Check Nginx config has /iceaa/uploads/ route
    if grep -q "location /iceaa/uploads/" /etc/nginx/sites-enabled/iceaa.conf 2>/dev/null; then
        log_pass "Nginx has /iceaa/uploads/ route configured"
    else
        log_fail "Nginx /iceaa/uploads/ route not found in config"
    fi
    
    # Check CORS headers in config
    if grep -A 5 "location /iceaa/uploads/" /etc/nginx/sites-enabled/iceaa.conf 2>/dev/null | grep -q "Access-Control-Allow-Origin"; then
        log_pass "CORS headers configured for uploads"
    else
        log_warn "CORS headers not found in /iceaa/uploads/ route"
    fi
}

check_nginx_validity() {
    log_header "4. Nginx Configuration Validity"
    
    if nginx -t 2>&1 | grep -q "successful"; then
        log_pass "Nginx configuration is valid"
    else
        log_fail "Nginx configuration has errors:"
        nginx -t
    fi
}

check_cors_headers() {
    log_header "5. CORS Headers Test"
    
    # Test CORS headers from Nginx
    HEADERS=$(curl -s -I http://localhost/iceaa/uploads/ 2>/dev/null)
    
    if echo "$HEADERS" | grep -q "Access-Control-Allow-Origin"; then
        log_pass "CORS headers are present"
    else
        log_warn "CORS headers not found in response"
    fi
}

check_frontend_imageurl_utility() {
    log_header "6. Frontend Image URL Utility"
    
    IMAGEURL_FILE="/var/www/html/iceaa/ICE_AlumniConnect/react-app/src/utils/imageUrl.js"
    
    if [ -f "$IMAGEURL_FILE" ]; then
        log_pass "Image URL utility exists: imageUrl.js"
        
        # Check for key functions
        if grep -q "export function getImageUrl" "$IMAGEURL_FILE"; then
            log_pass "getImageUrl() function found"
        fi
        
        if grep -q "export function getUploadsBaseUrl" "$IMAGEURL_FILE"; then
            log_pass "getUploadsBaseUrl() function found"
        fi
    else
        log_fail "Image URL utility not found: $IMAGEURL_FILE"
    fi
}

check_profile_image_component() {
    log_header "7. Profile Image Component"
    
    PROFILE_COMPONENT="/var/www/html/iceaa/ICE_AlumniConnect/react-app/src/components/ProfileImage.jsx"
    
    if [ -f "$PROFILE_COMPONENT" ]; then
        log_pass "Profile Image component exists"
        
        if grep -q "crossOrigin" "$PROFILE_COMPONENT"; then
            log_pass "CORS (crossOrigin) attribute configured"
        else
            log_warn "CORS (crossOrigin) attribute not found"
        fi
    else
        log_fail "Profile Image component not found: $PROFILE_COMPONENT"
    fi
}

check_frontend_env() {
    log_header "8. Frontend Environment"
    
    ENV_FILE="/var/www/html/iceaa/ICE_AlumniConnect/react-app/.env.production"
    
    if [ -f "$ENV_FILE" ]; then
        log_pass "Frontend .env.production exists"
        
        if grep -q "VITE_BASE_URL=/iceaa/" "$ENV_FILE"; then
            log_pass "VITE_BASE_URL is set to /iceaa/"
        fi
    else
        log_warn ".env.production not found (using defaults should be OK)"
    fi
}

check_react_build() {
    log_header "9. React Build"
    
    DIST_PATH="/var/www/html/iceaa/ICE_AlumniConnect/react-app/dist"
    
    if [ -d "$DIST_PATH" ]; then
        log_pass "React build directory exists"
        
        if [ -f "$DIST_PATH/index.html" ]; then
            log_pass "React index.html exists"
        else
            log_fail "React index.html not found"
        fi
        
        if ls "$DIST_PATH/assets/"*.js >/dev/null 2>&1; then
            JS_COUNT=$(ls "$DIST_PATH/assets/"*.js 2>/dev/null | wc -l)
            log_pass "React JS assets exist: $JS_COUNT files"
        else
            log_warn "No JS assets found in dist/assets/"
        fi
    else
        log_fail "React build not found: $DIST_PATH"
    fi
}

check_api_endpoint() {
    log_header "10. API Endpoint"
    
    # Check if API is responding
    API_RESPONSE=$(curl -s http://localhost/iceaa/api/health 2>/dev/null || echo "FAILED")
    
    if echo "$API_RESPONSE" | grep -q "success"; then
        log_pass "API health check passed"
    else
        log_warn "API response: $API_RESPONSE"
    fi
}

# ============================================================================
# Summary
# ============================================================================

print_summary() {
    log_header "Summary"
    
    TOTAL=$((CHECKS_PASSED + CHECKS_FAILED))
    
    echo ""
    echo "  ✓ Passed:  $CHECKS_PASSED"
    echo "  ✗ Failed:  $CHECKS_FAILED"
    echo "  ─────────────"
    echo "  Total:   $TOTAL"
    echo ""
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✓ All image checks passed!${NC}"
        echo -e "${GREEN}Images and uploads are ready for production.${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
        return 0
    else
        echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}⚠ Some checks failed or have warnings.${NC}"
        echo -e "${YELLOW}Please review above and fix issues.${NC}"
        echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
        return 1
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         IMAGE & UPLOAD VERIFICATION                       ║${NC}"
    echo -e "${BLUE}║        AlumniConnect Production Deployment                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_upload_folder
    check_backend_upload_endpoint
    check_nginx_uploads_route
    check_nginx_validity
    check_cors_headers
    check_frontend_imageurl_utility
    check_profile_image_component
    check_frontend_env
    check_react_build
    check_api_endpoint
    
    print_summary
}

main "$@"
