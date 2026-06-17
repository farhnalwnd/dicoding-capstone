"""
Admin Seed Script
=================
Run this script to create the first Admin user in the database.

Usage (from the project root):
    python backend/seed_admin.py

Or inside Docker:
    docker-compose exec backend python seed_admin.py

Environment variables used:
    MONGO_URI    — MongoDB connection string (default: mongodb://admin:password@localhost:27017/)
    ADMIN_NAME   — Admin display name (default: Super Admin)
    ADMIN_EMAIL  — Admin email (default: admin@smartrecruit.ai)
    ADMIN_PASS   — Admin password (min 8 chars, default: Admin@1234)
"""

import os
import sys

# Add the project root to sys.path so app modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone
from app.core.mongodb import get_users_collection
from app.core.auth import hash_password

ADMIN_NAME  = os.getenv("ADMIN_NAME",  "Super Admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@smartrecruit.ai")
ADMIN_PASS  = os.getenv("ADMIN_PASS",  "Admin@1234")

def seed():
    users = get_users_collection()

    existing = users.find_one({"email": ADMIN_EMAIL})
    if existing:
        print(f"[SKIP] Admin user '{ADMIN_EMAIL}' already exists.")
        return

    users.insert_one({
        "name":       ADMIN_NAME,
        "email":      ADMIN_EMAIL,
        "password":   hash_password(ADMIN_PASS),
        "role":       "admin",
        "provider":   "email",
        "disabled":   False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login": None,
    })

    print(f"[OK] Admin user created:")
    print(f"     Email   : {ADMIN_EMAIL}")
    print(f"     Password: {ADMIN_PASS}")
    print(f"     Role    : admin")
    print()
    print("[!] Please change the default password immediately after first login.")

if __name__ == "__main__":
    seed()
