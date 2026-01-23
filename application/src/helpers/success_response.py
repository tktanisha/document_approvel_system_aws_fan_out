from fastapi.responses import JSONResponse

def write_success_response(status_code: int, data: any = None, message: str | None = None) -> JSONResponse:
    payload = {
        "status": True,
        "data": data
    }
    print("data ====", payload["data"])
    if message:
        payload["message"] = message
    return JSONResponse(
        status_code=status_code,
        content=payload,
    )
