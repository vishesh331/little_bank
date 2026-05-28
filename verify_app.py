#!/usr/bin/env python
"""Quick verification of movie streaming app setup"""
from app import app, MOVIES, MOVIE_SELLER_ACCOUNT

print('✓ App initialized successfully')
print(f'✓ Movies loaded: {len(MOVIES)} from JSON')
print(f'✓ Seller account: {MOVIE_SELLER_ACCOUNT}')
print()
print('Movie List:')
for m in MOVIES:
    print(f"  {m['id']}: {m['title']} - {m['genre']} - YouTube: {m['youtube_id']}")
print()
print('All configurations verified!')
