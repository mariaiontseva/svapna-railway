#!/usr/bin/env python3
"""
Initialize database for Railway deployment
Downloads the database from GitHub Release if not present
"""

import os
import urllib.request
import sys

DATABASE_PATH = '/app/muktabodha_texts.db'
DATABASE_URL = 'https://github.com/mariaiontseva/svapna-railway/releases/download/v1.0/muktabodha_texts.db'

def download_database():
    """Download database from GitHub Release"""
    if os.path.exists(DATABASE_PATH):
        print(f"✓ Database already exists at {DATABASE_PATH}")
        return
    
    print(f"📥 Downloading database from GitHub Release...")
    print(f"   URL: {DATABASE_URL}")
    print(f"   Size: ~150MB")
    
    try:
        # Download with progress
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100.0 / total_size, 100)
            sys.stdout.write(f'\r   Progress: {percent:.1f}%')
            sys.stdout.flush()
        
        urllib.request.urlretrieve(DATABASE_URL, DATABASE_PATH, download_progress)
        print(f"\n✓ Database downloaded successfully!")
        print(f"   Size: {os.path.getsize(DATABASE_PATH) / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"\n❌ Error downloading database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_database()