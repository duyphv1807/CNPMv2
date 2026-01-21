# supabase_client.py
from supabase import create_client, Client

# Thay bằng URL và KEY của bạn từ Supabase Project Settings
SUPABASE_URL = "https://tdkmoeyqaejiucanbgdj.supabase.co/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRka21vZXlxYWVqaXVjYW5iZ2RqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODAzMDAwMCwiZXhwIjoyMDgzNjA2MDAwfQ.NQBxr2uL7wKN6xbAwzCuciW27k0bDAWri6rervA5rHw"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

