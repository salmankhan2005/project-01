#!/usr/bin/env python3
"""
Test script to check admin recipes
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check admin_recipes table
try:
    result = supabase.table('admin_recipes').select('*').execute()
    print(f"Admin recipes count: {len(result.data)}")
    for recipe in result.data:
        print(f"- {recipe.get('title')} (Status: {recipe.get('status')})")
except Exception as e:
    print(f"Error: {e}")

# Test discover endpoint
import requests
try:
    response = requests.get('http://127.0.0.1:5000/api/discover/recipes')
    if response.ok:
        data = response.json()
        print(f"\nDiscover recipes count: {len(data.get('recipes', []))}")
        admin_recipes = [r for r in data.get('recipes', []) if r.get('is_admin_recipe')]
        print(f"Admin recipes in discover: {len(admin_recipes)}")
    else:
        print(f"Discover endpoint error: {response.status_code}")
except Exception as e:
    print(f"Request error: {e}")