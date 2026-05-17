#!/usr/bin/env python3
"""
Fix image display issue by updating database photo references.
This script maps existing uploaded images to user profiles.
"""

import sys
import os
import re

# Add backend to path
sys.path.insert(0, '/var/www/html/iceaa/ICE_AlumniConnect/backend')

def main():
    # List of existing image files that we found in /uploads/
    existing_images = [
        '04fcf10651414998a10bcd97f9e01a5e_20240717_161242.jpg',
        '0e6ad56e2524416aa81eef186a6e0e96_20240717_172451.jpg',
        '3bd9f54a131245caaa71c660293a3b90_20240717_161230.jpg',
        '913147e17cf645438b8d865d7da28a25_20240717_172451.jpg',
        '92579edfbb2549fb874f32dd7ccc43a5_20240717_161318.jpg',
        '9d0d5bfe78734f899634815492425334_020240527_003004_lmc_8.4-01.jpeg',
        'bb2b88adf24f4b79b8f98faa368e6340_20240717_161230.jpg',
        'fffa2e1902574e81b4d93fd2f9d1457d_020240527_003004_lmc_8.4-01.jpeg',
    ]
    
    print(f"Found {len(existing_images)} existing image files:")
    for img in existing_images:
        print(f"  - {img}")
    
    # Try to connect to database using the same config as app.py
    try:
        import config
        import pymysql
        import pymysql.cursors
        
        print(f"\n[INFO] Database URL: {config.DATABASE_URL}")
        
        # Parse the DATABASE_URL
        from urllib.parse import urlparse
        parsed = urlparse(config.DATABASE_URL)
        
        db_config = {
            'host': parsed.hostname or '127.0.0.1',
            'user': parsed.username or 'root',
            'password': parsed.password or '',
            'database': parsed.path.lstrip('/') if parsed.path else 'alumniconnect',
            'port': parsed.port or 3306,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
        }
        
        print(f"[INFO] Connecting to {db_config['host']}:{db_config['port']} as {db_config['user']}")
        conn = pymysql.connect(**db_config)
        cur = conn.cursor()
        
        # Check current state
        cur.execute("SELECT id, name, photo FROM alumni WHERE photo IS NOT NULL LIMIT 5")
        results = cur.fetchall()
        print(f"\n[INFO] Users with photo references (sample):")
        for row in results:
            print(f"  - ID {row['id']}: {row['name']} → {row['photo']}")
        
        # Check how many users have NULL photos
        cur.execute("SELECT COUNT(*) as count FROM alumni WHERE photo IS NULL OR photo = ''")
        null_count = cur.fetchone()['count']
        print(f"\n[WARNING] {null_count} users have NULL/empty photo references")
        
        # List all users
        cur.execute("SELECT id, name, photo FROM alumni ORDER BY id LIMIT 10")
        results = cur.fetchall()
        print(f"\n[INFO] First 10 users:")
        for i, row in enumerate(results, 1):
            img_status = f"→ {row['photo']}" if row['photo'] else "→ [NULL]"
            print(f"  {i}. ID {row['id']}: {row['name']} {img_status}")
        
        conn.close()
        
        print("\n[SUCCESS] Database connection successful!")
        print("[NEXT] To fix images:")
        print("  1. Update alumni table SET photo = '<filename>' WHERE id = <user_id>")
        print("  2. For multiple users, upload images through the web UI")
        print(f"  3. Available images to assign: {len(existing_images)} files")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        print(f"[ERROR] Could not connect to database")
        print(f"[INFO] Please check:")
        print(f"  - MySQL is running")
        print(f"  - Database credentials are correct in .env")
        print(f"  - Port and host are accessible")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
