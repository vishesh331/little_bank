"""
Test script for movie streaming app
"""
import sys
from pathlib import Path

# Add path to parent
sys.path.insert(0, str(Path(__file__).parent))

import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# Test 1: Verify app initialization
print("=" * 60)
print("TEST 1: Verify app can initialize")
print("=" * 60)

try:
    from movie_streaming.app import app, MOVIES, _ensure_seller_account
    print(f"✓ App initialized successfully")
    print(f"✓ Loaded {len(MOVIES)} movies from JSON")
    
    if len(MOVIES) == 0:
        print("✗ ERROR: No movies loaded!")
        sys.exit(1)
    
    print("\nMovie list:")
    for movie in MOVIES[:3]:
        print(f"  - {movie['title']} (ID: {movie['youtube_id']})")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Verify seller account setup
print("\n" + "=" * 60)
print("TEST 2: Verify seller account setup")
print("=" * 60)

try:
    _ensure_seller_account()
    from movie_streaming.app import MOVIE_SELLER_ACCOUNT
    if MOVIE_SELLER_ACCOUNT:
        print(f"✓ Seller account created/found: {MOVIE_SELLER_ACCOUNT}")
    else:
        print("✗ ERROR: Seller account not initialized!")
        sys.exit(1)
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verify app routes
print("\n" + "=" * 60)
print("TEST 3: Verify app routes")
print("=" * 60)

try:
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    expected_routes = ['/login', '/catalog', '/api/movie/', '/api/process-payment', '/watch/']
    
    for expected in expected_routes:
        found = any(expected in route for route in routes)
        status = "✓" if found else "✗"
        print(f"{status} Route {expected}")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

# Test 4: Verify movie data structure
print("\n" + "=" * 60)
print("TEST 4: Verify movie data structure")
print("=" * 60)

try:
    required_fields = ['id', 'title', 'price', 'description', 'thumbnail', 'video_url', 'youtube_id', 'rating', 'genre']
    
    for movie in MOVIES:
        missing = [f for f in required_fields if f not in movie]
        if missing:
            print(f"✗ Movie '{movie.get('title', 'UNKNOWN')}' missing fields: {missing}")
            sys.exit(1)
    
    print(f"✓ All {len(MOVIES)} movies have required fields")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
