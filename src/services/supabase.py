import os
from supabase import create_client, Client

SUPABASE_URL: str = os.environ.get("SUPABASE_URL") or ""
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY") or ""

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
