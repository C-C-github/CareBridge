#!/usr/bin/env python
"""
Delete user by username
"""

import os, sys, django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_system.settings')

django.setup()
from django.contrib.auth import get_user_model

if len(sys.argv) > 1:
    username = sys.argv[1]
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        user.delete()
        print(f"✅ User '{username}' deleted successfully!")
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
else:
    print("Usage: python delete_user_by_username.py <username>")
    print("Example: python delete_user_by_username.py satkuri")
