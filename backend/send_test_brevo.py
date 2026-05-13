import json
import sys
from urllib import request as urllib_request, error as urllib_error
import config

def main():
    if len(sys.argv) < 2:
        print('Usage: python send_test_brevo.py recipient@example.com')
        return 2

    recipient = sys.argv[1]
    if not config.BREVO_API_KEY:
        print('BREVO_API_KEY not configured in backend/.env or environment')
        return 3

    if not config.SMTP_FROM_EMAIL:
        print('SMTP_FROM_EMAIL not configured in backend/.env or environment')
        return 4

    payload = {
        'sender': {'name': config.SMTP_FROM_NAME or 'AlumniConnect', 'email': config.SMTP_FROM_EMAIL},
        'to': [{'email': recipient}],
        'subject': 'Brevo quick test',
        'textContent': 'This is a quick Brevo test sent from the local workspace script.',
        'htmlContent': '<p>This is a quick <strong>Brevo</strong> test sent from the local workspace script.</p>',
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib_request.Request(
        config.BREVO_API_URL,
        data=data,
        method='POST',
        headers={
            'accept': 'application/json',
            'content-type': 'application/json',
            'api-key': config.BREVO_API_KEY,
        },
    )

    try:
        with urllib_request.urlopen(req, timeout=max(5, int(config.BREVO_TIMEOUT or 20))) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            print('Status:', getattr(resp, 'status', None))
            print('Response body:', body)
            return 0
    except urllib_error.HTTPError as ex:
        body = ex.read().decode('utf-8', errors='ignore') if hasattr(ex, 'read') else ''
        print(f'HTTPError {ex.code}: {body[:1000]}')
        return 5
    except urllib_error.URLError as ex:
        print('URLError:', ex.reason)
        return 6
    except Exception as ex:
        print('Error:', ex)
        return 7

if __name__ == '__main__':
    sys.exit(main())
