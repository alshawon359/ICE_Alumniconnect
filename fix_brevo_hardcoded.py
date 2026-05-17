#!/usr/bin/env python3
"""
Patch app.py to use hardcoded Brevo credentials instead of .env
This ensures 100% working email delivery
"""

import re

# Read the current app.py
with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the _send_email_via_brevo function
# We'll replace from the function definition to its return statement

old_pattern = r'def _send_email_via_brevo\(recipients, subject, plain_content, html_content\):.*?return \{\'sent\': sent_count, \'failed\': failed_count, \'errors\': errors\}'

new_function = '''def _send_email_via_brevo(recipients, subject, plain_content, html_content):
    """Send email via Brevo API with hardcoded credentials."""
    sent_count = 0
    failed_count = 0
    errors = []
    
    # ===== HARDCODED BREVO CREDENTIALS (Production - DO NOT CHANGE) =====
    BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')  # Set in .env.production
    BREVO_SENDER_EMAIL = 'iceaa.ru.2000@gmail.com'
    BREVO_SENDER_NAME = 'ICEAA Alumni Connect'
    BREVO_API_URL = 'https://api.brevo.com:443/v3/smtp/email'  # Explicit port 443
    
    timeout = 20
    plain_only_domains = {
        d.strip().lower()
        for d in (getattr(config, 'MAIL_PLAIN_ONLY_DOMAINS', None) or [])
        if d and d.strip()
    }
    custom_headers = _mail_metadata_headers()
    
    print(f'[EMAIL] Brevo send: {len(recipients)} recipients, subject: {subject[:50]}...')
    print(f'[EMAIL] Sender: {BREVO_SENDER_EMAIL}, API: {BREVO_API_URL}')

    # Validate configuration
    if not BREVO_API_KEY or not BREVO_API_KEY.strip():
        error_msg = 'Brevo API key is hardcoded but empty'
        print(f'[EMAIL ERROR] {error_msg}')
        for email in recipients:
            errors.append({'email': email, 'error': error_msg})
        return {'sent': 0, 'failed': len(recipients), 'errors': errors}

    if not BREVO_SENDER_EMAIL or '@' not in BREVO_SENDER_EMAIL:
        error_msg = 'Invalid sender email (hardcoded). Check code.'
        print(f'[EMAIL ERROR] {error_msg}')
        for email in recipients:
            errors.append({'email': email, 'error': error_msg})
        return {'sent': 0, 'failed': len(recipients), 'errors': errors}

    for email in recipients:
        domain = email.rsplit('@', 1)[-1].strip().lower() if '@' in email else ''
        plain_only = bool(domain and domain in plain_only_domains)

        payload = {
            'sender': {'name': BREVO_SENDER_NAME, 'email': BREVO_SENDER_EMAIL},
            'to': [{'email': email}],
            'subject': str(subject or ''),
            'textContent': plain_content,
            'replyTo': {'email': BREVO_SENDER_EMAIL},
            'headers': custom_headers,
            'tags': ['alumniconnect-broadcast'],
        }
        if payload.get('tags') is None:
            payload.pop('tags', None)
        if not plain_only:
            payload['htmlContent'] = html_content
        
        # Filter out None/empty values from headers to prevent Brevo validation errors
        filtered_headers = {k: v for k, v in custom_headers.items() if v}
        payload['headers'] = filtered_headers

        data = json.dumps(payload).encode('utf-8')

        # Small retry window for transient Brevo API/network issues.
        sent = False
        last_error = 'unknown error'
        first_401_error = None
        
        for attempt in range(3):
            req = urllib_request.Request(
                BREVO_API_URL,
                data=data,
                method='POST',
                headers={
                    'accept': 'application/json',
                    'content-type': 'application/json',
                    'api-key': BREVO_API_KEY,
                },
            )
            try:
                with urllib_request.urlopen(req, timeout=timeout) as resp:
                    status = getattr(resp, 'status', 0)
                    if 200 <= status < 300:
                        sent = True
                        print(f'[EMAIL] ✓ Sent to {email} via Brevo API (status {status})')
                        break
                    last_error = f'Brevo returned status {status}'
                    print(f'[EMAIL] ✗ Failed to send to {email}: status {status}')
            except urllib_error.HTTPError as ex:
                body = ex.read().decode('utf-8', errors='ignore') if hasattr(ex, 'read') else ''
                
                # Handle authentication errors specifically
                if ex.code == 401:
                    if first_401_error is None:
                        first_401_error = body
                    last_error = 'Brevo API authentication failed. Verify BREVO_API_KEY is enabled and valid.'
                    if 'not enabled' in body.lower() or 'unauthorized' in body.lower():
                        last_error += ' (API Key is not enabled in Brevo account)'
                    print(f'[EMAIL ERROR] Auth failed for {email}: {last_error}')
                    break  # Don't retry on auth failures
                
                last_error = f'Brevo HTTP {ex.code}: {body[:220]}'
                print(f'[EMAIL] HTTP {ex.code} for {email}, attempt {attempt + 1}/3: {body[:100]}')
                if ex.code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(1 + attempt)
                    continue
                break
            except urllib_error.URLError as ex:
                last_error = f'Brevo network error: {ex.reason}'
                print(f'[EMAIL] Network error for {email}, attempt {attempt + 1}/3: {ex.reason}')
                if attempt < 2:
                    time.sleep(1 + attempt)
                    continue
                break
            except Exception as ex:
                last_error = str(ex)
                print(f'[EMAIL] Exception for {email}: {str(ex)}')
                break

        if sent:
            sent_count += 1
        else:
            failed_count += 1
            errors.append({'email': email, 'error': last_error})
            print(f'[EMAIL] ✗ Failed to send to {email}: {last_error}')

    print(f'[EMAIL] Summary: Sent {sent_count}/{len(recipients)}, Failed {failed_count}/{len(recipients)}')
    return {'sent': sent_count, 'failed': failed_count, 'errors': errors}'''

# Replace using regex with DOTALL flag
content = re.sub(old_pattern, new_function, content, flags=re.DOTALL)

# Write back
with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ app.py updated with hardcoded Brevo credentials")
print("✓ Run: scp -P 36109 backend/app.py root@172.30.240.39:/var/www/html/iceaa/ICE_AlumniConnect/backend/app.py")
print("✓ Then SSH and: systemctl restart alumniconnect")
