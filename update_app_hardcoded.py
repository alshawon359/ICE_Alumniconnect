#!/usr/bin/env python3
"""
Update app.py with hardcoded Brevo credentials
Run locally: python update_app_hardcoded.py
Then copy the result to server: scp -P 36109 backend/app.py root@172.30.240.39:/var/www/html/iceaa/ICE_AlumniConnect/backend/
"""

import re

# Read the entire app.py file
with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the _send_email_via_brevo function and replace it
# Pattern: from "def _send_email_via_brevo..." to the next "def " at same indentation level

old_function_pattern = r'def _send_email_via_brevo\(recipients, subject, plain_content, html_content\):.*?(?=\ndef _send_email_via_smtp)'

new_function = '''def _send_email_via_brevo(recipients, subject, plain_content, html_content):
    """Send email via Brevo API with hardcoded credentials (100% production reliable)."""
    sent_count = 0
    failed_count = 0
    errors = []
    
    # ===== HARDCODED BREVO CREDENTIALS (Production) =====
    BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')  # Set in .env.production
    BREVO_SENDER_EMAIL = 'iceaa.ru.2000@gmail.com'
    BREVO_SENDER_NAME = 'ICEAA Alumni Connect'
    BREVO_API_URL = 'https://api.brevo.com:443/v3/smtp/email'
    timeout = 20
    
    plain_only_domains = {
        d.strip().lower()
        for d in (getattr(config, 'MAIL_PLAIN_ONLY_DOMAINS', None) or [])
        if d and d.strip()
    }
    custom_headers = _mail_metadata_headers()
    
    print(f'[EMAIL] Brevo send: {len(recipients)} recipients, subject: {subject[:50]}...')
    print(f'[EMAIL] Using hardcoded: {BREVO_SENDER_EMAIL}, API: {BREVO_API_URL}')

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
        
        filtered_headers = {k: v for k, v in custom_headers.items() if v}
        payload['headers'] = filtered_headers

        data = json.dumps(payload).encode('utf-8')

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
                
                if ex.code == 401:
                    if first_401_error is None:
                        first_401_error = body
                    last_error = 'Brevo API authentication failed. Verify hardcoded BREVO_API_KEY is valid.'
                    if 'not enabled' in body.lower() or 'unauthorized' in body.lower():
                        last_error += ' (API Key is not enabled in Brevo account)'
                    print(f'[EMAIL ERROR] Auth failed for {email}: {last_error}')
                    break
                
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
    return {'sent': sent_count, 'failed': failed_count, 'errors': errors}

'''

# Replace the function using regex with DOTALL flag
updated_content = re.sub(old_function_pattern, new_function, content, flags=re.DOTALL)

# Verify the replacement happened
if updated_content == content:
    print("ERROR: Could not find and replace the function!")
    print("Pattern may not have matched. Check the function signature.")
    exit(1)

# Write the updated content back to app.py
with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("✓ Successfully updated backend/app.py with hardcoded Brevo credentials")
print("")
print("NEXT STEPS (Run on Windows terminal):")
print("1. scp -P 36109 backend/app.py root@172.30.240.39:/var/www/html/iceaa/ICE_AlumniConnect/backend/app.py")
print("2. ssh -p 36109 root@172.30.240.39")
print("3. systemctl restart alumniconnect")
print("4. systemctl status alumniconnect")
print("")
print("Test via curl:")
print("curl -X POST http://127.0.0.1:5000/api/send-email \\")
print("  -H 'Content-Type: application/json' \\")
print("  -d '{\"email\":\"test@example.com\",\"subject\":\"Test\",\"message\":\"Test email\"}'")
