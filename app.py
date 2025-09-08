#!/usr/bin/env python3
"""
SVAPNA Search - Railway Deployment with Full Database
Complete Sanskrit text search with full 149MB database
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import json
import os
import time
import urllib.request
import sys

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_PATH = '/app/muktabodha_texts.db'  # Railway path
DATABASE_URL = 'https://github.com/mariaiontseva/svapna-railway/releases/download/v1.0/muktabodha_texts.db'

def ensure_database():
    """Ensure database exists, download if needed"""
    global DATABASE_PATH
    
    # Check Railway path first
    if os.path.exists(DATABASE_PATH):
        print(f"✓ Database found at {DATABASE_PATH}")
        return
    
    # Try local fallback
    local_path = '/Users/mariaiontseva/muktabodha_texts.db'
    if os.path.exists(local_path):
        DATABASE_PATH = local_path
        print(f"✓ Using local database at {DATABASE_PATH}")
        return
    
    # Download from GitHub Release
    print(f"📥 Downloading database from GitHub Release...")
    print(f"   URL: {DATABASE_URL}")
    print(f"   Target: {DATABASE_PATH}")
    
    try:
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
        print("   Falling back to demo mode...")
        DATABASE_PATH = None

# Initialize database on startup
ensure_database()

@app.route('/')
def dashboard():
    """Serve the search dashboard"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SVAPNA Sanskrit Search - Full Database</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            padding: 40px 20px;
            text-align: center;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
        }
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            flex: 1;
        }
        .search-box {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }
        .search-input {
            width: 100%;
            padding: 20px;
            font-size: 1.2rem;
            border: 2px solid #e2e8f0;
            border-radius: 15px;
            margin-bottom: 20px;
            color: #1e40af;
        }
        .search-input:focus {
            outline: none;
            border-color: #1e40af;
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        }
        .quick-tags {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .quick-tag {
            padding: 8px 16px;
            background: #f1f5f9;
            color: #475569;
            border-radius: 20px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-tag:hover {
            background: #1e40af;
            color: white;
        }
        .search-btn {
            background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .search-btn:hover {
            box-shadow: 0 10px 20px rgba(30, 64, 175, 0.3);
        }
        .results {
            background: white;
            border-radius: 20px;
            color: #1f2937;
            min-height: 400px;
        }
        .result-card {
            padding: 24px;
            border-bottom: 1px solid #f1f5f9;
        }
        .result-card:last-child {
            border-bottom: none;
        }
        .result-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 8px;
        }
        .result-meta {
            color: #64748b;
            margin-bottom: 12px;
        }
        .snippet {
            background: #f8fafc;
            padding: 16px;
            border-radius: 10px;
            border-left: 4px solid #1e40af;
            font-family: 'Noto Sans Devanagari', sans-serif;
            line-height: 1.6;
            margin-top: 12px;
        }
        .highlight {
            background: #fef08a;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 600;
        }
        .loading {
            text-align: center;
            padding: 60px;
            color: #64748b;
        }
        .spinner {
            border: 3px solid #f1f5f9;
            border-top: 3px solid #1e40af;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .search-info {
            padding: 20px;
            background: #f0f9ff;
            border-radius: 10px 10px 0 0;
            color: #1e40af;
            font-weight: 600;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <div class="header">
        <h1>SVAPNA Sanskrit Search</h1>
        <div class="subtitle">Complete Database • Full-Text Search • Railway Hosted</div>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">311</div>
                <div class="stat-label">Total Texts</div>
            </div>
            <div class="stat">
                <div class="stat-value">149MB</div>
                <div class="stat-label">Full Database</div>
            </div>
            <div class="stat">
                <div class="stat-value">0</div>
                <div class="stat-label" id="results-count">Search Results</div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="search-box">
            <input type="text" class="search-input" id="searchInput" 
                   placeholder="Search any Sanskrit term (e.g., svapnasvapna, yoga, tantra)..." 
                   value="svapnasvapna">
            
            <div class="quick-tags">
                <button class="quick-tag" onclick="quickSearch('svapna')">svapna</button>
                <button class="quick-tag" onclick="quickSearch('svapnasvapna')">svapnasvapna</button>
                <button class="quick-tag" onclick="quickSearch('svapnayoga')">svapnayoga</button>
                <button class="quick-tag" onclick="quickSearch('svapnajāgrat')">svapnajāgrat</button>
                <button class="quick-tag" onclick="quickSearch('svapnalabdha')">svapnalabdha</button>
                <button class="quick-tag" onclick="quickSearch('nidrā')">nidrā</button>
                <button class="quick-tag" onclick="quickSearch('suṣupti')">suṣupti</button>
            </div>
            
            <button class="search-btn" onclick="performSearch()">Search Full Database</button>
        </div>

        <div class="results" id="results">
            <div class="loading">
                <div class="spinner"></div>
                Ready to search 311 Sanskrit texts...
            </div>
        </div>
    </div>

    <script>
        // Search functionality
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });

        function quickSearch(term) {
            document.getElementById('searchInput').value = term;
            performSearch();
        }

        async function performSearch() {
            const searchTerm = document.getElementById('searchInput').value.trim();
            if (!searchTerm) return;

            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    Searching ${searchTerm} across 311 texts...
                </div>
            `;

            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ search_term: searchTerm })
                });

                const data = await response.json();
                displayResults(data.results, searchTerm, data.total_matches);
                
                // Update stats
                document.getElementById('results-count').textContent = data.results.length;
                document.querySelector('.stat-value').textContent = data.results.length;

            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="loading" style="color: #ef4444;">
                        Error searching database: ${error.message}
                    </div>
                `;
            }
        }

        function displayResults(results, searchTerm, totalMatches) {
            const resultsDiv = document.getElementById('results');
            
            if (results.length === 0) {
                resultsDiv.innerHTML = `
                    <div class="loading">
                        No results found for "${searchTerm}"
                    </div>
                `;
                return;
            }

            let html = `
                <div class="search-info">
                    Found ${results.length} text${results.length !== 1 ? 's' : ''} containing "${searchTerm}" • ${totalMatches} occurrence${totalMatches !== 1 ? 's' : ''}
                </div>
            `;

            results.forEach(result => {
                html += `
                    <div class="result-card">
                        <div class="result-title">${result.display_name}</div>
                        <div class="result-meta">
                            Author: ${result.author} • Tradition: ${result.tradition} • 
                            Occurrences: ${result.count}
                        </div>
                `;
                
                if (result.snippets && result.snippets.length > 0) {
                    result.snippets.slice(0, 3).forEach(snippet => {
                        const highlighted = snippet.replace(
                            new RegExp(`(${searchTerm})`, 'gi'),
                            '<span class="highlight">$1</span>'
                        );
                        html += `<div class="snippet">${highlighted}</div>`;
                    });
                }
                
                html += `</div>`;
            });

            resultsDiv.innerHTML = html;
        }

        // Initial search
        performSearch();
    </script>
</body>
</html>
    """)

@app.route('/search', methods=['POST'])
def search_api():
    """Full-text search API endpoint"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        search_term = data.get('search_term', '').strip().lower()
        
        if not search_term:
            return jsonify({'error': 'Search term required'}), 400
        
        if DATABASE_PATH is None:
            return jsonify({'error': 'Database not available. Please wait for download to complete.'}), 503
        
        # Connect to database
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Direct search in search_index (bypass FTS issues)
        cursor.execute("""
            SELECT t.display_name, t.tradition, t.author, t.period, si.content
            FROM search_index si 
            JOIN texts t ON si.filename = t.filename
            WHERE LOWER(si.content) LIKE ?
            ORDER BY t.display_name
            LIMIT 100
        """, (f'%{search_term}%',))
        
        results = []
        total_matches = 0
        
        for row in cursor.fetchall():
            content = row['content'] if row['content'] else ""
            
            # Count occurrences
            count = content.lower().count(search_term)
            total_matches += count
            
            # Extract more snippets
            snippets = []
            if content and search_term in content.lower():
                content_lower = content.lower()
                start = 0
                for _ in range(5):  # Up to 5 snippets
                    pos = content_lower.find(search_term, start)
                    if pos == -1:
                        break
                    
                    snippet_start = max(0, pos - 80)
                    snippet_end = min(len(content), pos + len(search_term) + 80)
                    snippet = content[snippet_start:snippet_end]
                    
                    # Clean up
                    snippet = ' '.join(snippet.split())
                    if snippet_start > 0:
                        snippet = '...' + snippet
                    if snippet_end < len(content):
                        snippet = snippet + '...'
                    
                    snippets.append(snippet)
                    start = pos + len(search_term)
            
            results.append({
                'display_name': row['display_name'],
                'tradition': row['tradition'] or 'Unknown',
                'author': row['author'] or 'Unknown', 
                'period': row['period'] or 'Unknown',
                'count': count,
                'snippets': snippets
            })
        
        conn.close()
        
        search_time = time.time() - start_time
        print(f"FULL DATABASE search for '{search_term}' completed in {search_time:.3f}s, found {len(results)} texts")
        
        return jsonify({
            'results': results,
            'total_matches': total_matches,
            'search_time': search_time,
            'database_type': 'FULL_149MB'
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if DATABASE_PATH and os.path.exists(DATABASE_PATH) else 'missing',
        'database_path': DATABASE_PATH,
        'type': 'FULL_DATABASE_149MB'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print("="*60)
    print("🚀 SVAPNA SEARCH - RAILWAY DEPLOYMENT")  
    print("="*60)
    print(f"Database: {DATABASE_PATH}")
    print(f"Port: {port}")
    print(f"Full 149MB database with zero truncation!")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=False)