import hashlib
from fastapi import Response


def set_cache_headers(resp: Response, body: bytes):
    etag = hashlib.sha256(body).hexdigest()
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "public, max-age=300"
