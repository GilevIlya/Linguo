import logging
import uuid
from time import perf_counter

logger = logging.getLogger("app")

async def logging_middleware(request, call_next):
    start_time = perf_counter()
    request_id = str(uuid.uuid4())

    logger.info(
        f"REQUEST | ID: {request_id} | "
        f"Method: {request.method} | "
        f"URL: {request.url.path} | "
        f"Query: {dict(request.query_params)} | "
        f"Client: {request.client.host if request.client else 'unknown'} | "
        f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
    )

    try:
        response = await call_next(request)

        process_time = perf_counter() - start_time
        logger.info(
            f"RESPONSE | ID: {request_id} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.3f}s"
        )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

    except Exception as e:
        process_time = perf_counter() - start_time
        logger.error(
            f"ERROR | ID: {request_id} | "
            f"Exception: {type(e).__name__} | "
            f"Message: {str(e)} | "
            f"Time: {process_time:.3f}s",
            exc_info=True
        )
        raise

    return response
