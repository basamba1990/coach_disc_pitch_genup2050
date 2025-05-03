from supabase import create_client

BUCKET_NAME = "pitch-videos"

supabase_url = None
supabase_key = None
supabase = None

def init_supabase(url, key):
    global supabase_url, supabase_key, supabase
    supabase_url = url
    supabase_key = key
    supabase = create_client(supabase_url, supabase_key)
    return supabase
