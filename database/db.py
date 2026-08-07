"""
Database connection module.

Responsibilities:
- Load environment variables
- Validate configuration
- Create and expose a reusable Supabase client

No business logic or database queries belong here.
"""

from dotenv import load_dotenv
from supabase import Client, create_client

import os


# Load environment variables from .env
load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL:
    raise ValueError(
        "Missing environment variable: SUPABASE_URL"
    )

if not SUPABASE_KEY:
    raise ValueError(
        "Missing environment variable: SUPABASE_KEY"
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)