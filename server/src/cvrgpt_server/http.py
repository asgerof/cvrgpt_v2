import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import settings

client = httpx.AsyncClient(timeout=httpx.Timeout(settings.request_timeout_s))


class UpstreamError(Exception):
    pass


class UpstreamNotFound(UpstreamError):
    pass


class RetryableError(Exception):
    """Errors that should trigger a retry"""

    pass


@retry(
    stop=stop_after_attempt(settings.provider_max_retries + 1),
    wait=wait_exponential(min=0.25, max=2),
    retry=retry_if_exception_type(RetryableError),
)
async def get_json(url: str, params: dict | None = None, headers: dict | None = None):
    try:
        r = await client.get(url, params=params, headers=headers)
        if r.status_code == 404:
            raise UpstreamNotFound(r.text)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        # Only retry on server errors (5xx), not client errors (4xx)
        if 500 <= e.response.status_code < 600:
            raise RetryableError(str(e)) from e
        else:
            raise UpstreamError(str(e)) from e
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
        # Network errors should be retried
        raise RetryableError(str(e)) from e
