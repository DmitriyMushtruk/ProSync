import uuid
import base64

def generate_short_id(project_name: str, unique_id: str, length: int = 4) -> str:
    abbreviation = ''.join(word[0] for word in project_name.split() if word).upper()

    if isinstance(unique_id, str):
        uuid_obj = uuid.UUID(unique_id)
    else:
        uuid_obj = unique_id

    uuid_bytes = uuid_obj.bytes
    encoded = base64.urlsafe_b64encode(uuid_bytes).decode('utf-8').rstrip('=')
    short_id = encoded[:length].upper()

    return f"[{abbreviation}-{short_id}]"