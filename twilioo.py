import os
import json
from twilio.rest import Client
from datetime import datetime, timezone

# Environment vars:
#   export TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#   export TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ACCOUNT_SID = ""
AUTH_TOKEN = ""

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Optional: set a TTL in seconds (default is Twilio's default; you can set e.g., 3600 for 1 hour)
# token = client.tokens.create(ttl=3600)
token = client.tokens.create()

# token.ice_servers is an array of dicts:
#   { "urls": "stun:...", "username": "...", "credential": "..." } or urls: [ ... ]
# Normalize to single-string urls entries and include username/credential on TURN entries

ice_servers_out = []
username_for_turn = None
credential_for_turn = None

for s in token.ice_servers:
    urls = s.get("urls")
    # Twilio sometimes returns a list; normalize to individual entries
    if isinstance(urls, list):
        url_list = urls
    else:
        url_list = [urls]

    for u in url_list:
        entry = {"urls": u}
        if "turn:" in u or "turns:" in u:
            # Include credentials for TURN
            if s.get("username"):
                entry["username"] = s["username"]
                username_for_turn = s["username"]
            if s.get("credential"):
                entry["credential"] = s["credential"]
                credential_for_turn = s["credential"]
        ice_servers_out.append(entry)

# Build top-level fields in your desired shape
# Choose a representative username/password from the TURN creds if present
# (Twilio uses the same cred pair for all TURN entries in a single token)
username = username_for_turn or ""
password = credential_for_turn or ""

# date fields from token are datetimes; format to RFC 2822-like string as in your example
def fmt_dt(dt):
    if not dt:
        return None
    if isinstance(dt, str):
        return dt
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z").replace("+0000", "+0000").replace(" +0000", " +0000")

out = {
    "username": username,
    "ice_servers": ice_servers_out,
    "date_updated": fmt_dt(token.date_updated),
    "account_sid": token.account_sid,
    "ttl": str(token.ttl) if getattr(token, "ttl", None) is not None else None,
    "date_created": fmt_dt(token.date_created),
    "password": password,
}

print(json.dumps(out, indent=2))
