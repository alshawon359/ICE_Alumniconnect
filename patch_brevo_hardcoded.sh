#!/bin/bash
# Update app.py with hardcoded Brevo credentials on the server
# Run this on the server (already SSH'd in)

cd /var/www/html/iceaa/ICE_AlumniConnect/backend

# Backup
cp app.py app.py.backup.$(date +%s)

# Create updated function using Python here-document
python3 << 'PYTHON_EOF'
import json

# Read the file
with open('app.py', 'r') as f:
    lines = f.readlines()

# Find the line number where _send_email_via_brevo starts (line 1254 is index 1253)
start_idx = None
for i, line in enumerate(lines):
    if 'def _send_email_via_brevo(recipients, subject, plain_content, html_content):' in line:
        start_idx = i
        break

# Find the line where it ends (where the next function starts)
end_idx = None
for i in range(start_idx + 1, len(lines)):
    if lines[i].startswith('def _send_email_via_smtp'):
        end_idx = i
        break

if start_idx is not None and end_idx is not None:
    # New function with hardcoded credentials
    new_function = '''def _send_email_via_brevo(recipients, subject, plain_content, html_content):
    """Send email via Brevo API with hardcoded credentials."""
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
                        print(f'[EMAIL] ✓ Sent to {email} (status {status})')
                        break
                    last_error = f'Status {status}'
            except urllib_error.HTTPError as ex:
                body = ex.read().decode('utf-8', errors='ignore') if hasattr(ex, 'read') else ''
                if ex.code == 401:
                    last_error = 'Auth failed: API key issue'
                    print(f'[EMAIL ERROR] {last_error}')
                    break
                last_error = f'HTTP {ex.code}'
                if ex.code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(1 + attempt)
                    continue
                break
            except urllib_error.URLError as ex:
                last_error = f'Network error: {ex.reason}'
                if attempt < 2:
                    time.sleep(1 + attempt)
                    continue
                break
            except Exception as ex:
                last_error = str(ex)
                break

        if sent:
            sent_count += 1
        else:
            failed_count += 1
            errors.append({'email': email, 'error': last_error})

    print(f'[EMAIL] Summary: {sent_count}/{len(recipients)} sent, {failed_count} failed')
    return {'sent': sent_count, 'failed': failed_count, 'errors': errors}

'''
    
    # Replace the function
    new_lines = lines[:start_idx] + [new_function + '\n'] + lines[end_idx:]
    
    # Write back
    with open('app.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✓ Successfully patched _send_email_via_brevo() with hardcoded credentials")
    print("✓ Changes made at lines", start_idx+1, "to", end_idx)
else:
    print("ERROR: Could not find function boundaries")

PYTHON_EOF

# Restart service
echo "Restarting alumniconnect service..."
systemctl restart alumniconnect
sleep 2

# Check status
systemctl status alumniconnect

echo ""
echo "✓ Done! Service restarted with hardcoded Brevo credentials"
echo "✓ Test by sending an email from the app"
