
import hashlib


def generate_cache_key(request, vary_on_user=False):
    method = request.method
    path = request.get_full_path()

    raw_key = f"{method}:{path}"

    if vary_on_user:
        user = getattr(request, "user", None)
        user_id = getattr(user, "pk", None)

        raw_key += f":user:{user_id}"

    hashed_key = hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()

    return f"smart_cache:{hashed_key}"
