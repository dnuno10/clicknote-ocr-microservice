from datetime import datetime, timezone
from typing import Optional, Dict, Any

from ...db.client import supabase

def get_api_client(api_key: str) -> Optional[Dict[str, Any]]:
    try:
        api_key = api_key.strip()
        
        result = supabase.from_("api_clients").select("*").eq("apiKey", api_key).limit(1).execute()
        
        if not result.data or len(result.data) == 0:
            return None
            
        return result.data[0]
    except Exception as e:
        print(f"[ERROR] Error fetching API client: {e}")
        return None

def update_usage_counter(client_id: int, increment: int = 1) -> None:
    try:
        api_client = supabase.from_("api_clients").select("*").eq("idAPI", client_id).single().execute()
        if not api_client.data:
            return
            
        supabase.from_("api_clients").update({
            "lastUsedAt": datetime.now(timezone.utc).isoformat(),
            "usageCounter": api_client.data["usageCounter"] + increment
        }).eq("idAPI", client_id).execute()
    except Exception as e:
        print(f"[ERROR] Error updating API client usage: {e}")