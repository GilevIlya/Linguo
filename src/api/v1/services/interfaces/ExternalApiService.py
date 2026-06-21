import logging
from typing import Any
import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from api.v1.configs.external_api import ExternalAPIConfig
from api.v1.services.exceptions.base_exceptions import BusinessLogicException, NotFoundException
from api.v1.services.exceptions.error_codes.external_api_error_codes import ExternalAPIErrorCodes

logger = logging.getLogger("app")


async def log_request(request: httpx.Request) -> None:
    request.headers
    logger.info(
        "➡ [HTTP REQ] method=%s url=%s content_length=%s",
        request.method,
        request.url,
        request.headers.get("content-length", "unknown"),
    )


async def log_response(response: httpx.Response) -> None:
    await response.aread()
    logger.info(
        "⬅ [HTTP RES] status=%s url=%s duration=%.3fs retry_attempt=%s content_length=%s",
        response.status_code,
        response.url,
        response.elapsed.total_seconds(),
        response.request.extensions.get("retry_attempt", 0),
        len(response.content),
    )


class ExternalAPIService:
    def __init__(self, config: ExternalAPIConfig) -> None:
        self._client = httpx.AsyncClient(
            base_url=config.EXTERNAL_API_BASE_URL,
            timeout=httpx.Timeout(config.EXTERNAL_API_TIMEOUT),
            event_hooks={"request": [log_request], "response": [log_response]}
        )
        self.max_retries = config.EXTERNAL_API_RETRY_ATTEMPTS
        self.retry_delay = config.EXTERNAL_API_RETRY_DELAY

    def _get_retry_decorator(self) -> Any:
        return retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_fixed(self.retry_delay),
            retry=retry_if_exception(
                lambda e: isinstance(e, BusinessLogicException) 
                and e.error_code == ExternalAPIErrorCodes.UNAVAILABLE.value
            ),
            reraise=True,
            before_sleep=lambda retry_state: logger.warning(
                f"Attempt failed. Retrying in {self.retry_delay}s... (Attempt #{retry_state.attempt_number})"
            )
        )

    async def _request(
        self, method: str, path: str, params: dict | None = None, json: dict | None = None
    ) -> dict[str, Any] | None:
        
        @self._get_retry_decorator()
        async def _execute_with_retry():
            try:
                response = await self._client.request(method, path, params=params, json=json)
                
                if response.status_code == 404:
                    raise NotFoundException(
                        error_code=ExternalAPIErrorCodes.NOT_FOUND.value,
                        message=f"Resource not found at {response.url}",
                    )
                
                response.raise_for_status() 
                return response.json() if response.content else None

            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                logger.error(f"HTTP status error: {status_code} at {exc.request.url}")
                
                if status_code >= 500:
                    raise BusinessLogicException(
                        error_code=ExternalAPIErrorCodes.UNAVAILABLE.value,
                        message=f"External service unavailable: {status_code}. Details: {exc.response.text}"
                    )
                raise BusinessLogicException(
                    error_code=ExternalAPIErrorCodes.CLIENT_ERROR.value,
                    message=f"Client error: {status_code}. Details: {exc.response.text}"
                )

            except httpx.RequestError as exc:
                logger.error(f"Network error occurred while requesting {exc.request.url}: {exc}")
                raise BusinessLogicException(
                    error_code=ExternalAPIErrorCodes.UNAVAILABLE.value,
                    message=f"Network issue during external request: {exc}"
                )

        return await _execute_with_retry()

    async def close(self) -> None:
        await self._client.aclose()

    async def get(self, path: str, params: dict | None = None) -> dict[str, Any] | None:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, body: dict | None = None) -> dict[str, Any] | None:
        return await self._request("POST", path, json=body)

    async def put(self, path: str, body: dict | None = None) -> dict[str, Any] | None:
        return await self._request("PUT", path, json=body)

    async def patch(self, path: str, body: dict | None = None) -> dict[str, Any] | None:
        return await self._request("PATCH", path, json=body)

    async def delete(self, path: str) -> dict[str, Any] | None:
        return await self._request("DELETE", path)