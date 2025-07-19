import traceback
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI, 
    HTTPException, 
    Request, 
    Depends, 
    status
)
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.schemas import (
    ModelRequest, 
    ModelResponse, 
    HealthCheck, 
    ValidationErrorResponse,
    UnauthorizedErrorResponse,
    ServerErrorResponse
)
from src.config import (
    logger,
    model,
    data_client,
    CORRECT_USERNAME,
    CORRECT_PASSWORD,
    HOST,
    PORT,
    data_collection_executor
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown processes."""

    # startup
    logger.info("Launching app...")
    logger.info(f"App running on http://{HOST}:{PORT}")
    logger.info("Awaiting requests...")

    yield

    # shutdown
    logger.info("Shutting down app...")
    logger.info("Closing DataCollectionClient...")
    data_client.close()
    logger.info(f"DataCollectionClient closed successfully.")
    logger.info("App shut down.")


app = FastAPI(
    title="Logistic Regression Model",
    summary="Returns predicted probabilities.",
    version="1.0.0",
    lifespan=lifespan
)

security = HTTPBasic()


# ---------- SUPPORT FUNCS ----------


def log_request(request: Request):
    """Logs the endpoint being called."""
    
    logger.info(f"Endpoint called: {request.method} {request.url.path}")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Authenticate the user based on the provided credentials.

    This function checks if the provided username and password match
    the expected values. If the credentials are invalid, an HTTP 401
    Unauthorized error is raised.
    """

    if credentials.username != CORRECT_USERNAME or credentials.password != CORRECT_PASSWORD:
        logger.error(f"User '{credentials.username}' cannot be authenticated.")
        logger.error("Response status: 401")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Custom handler for validation errors.
    
    FastAPI will handle validation errors using this handler. If 
    the request body does not match the ModelInput schema, we return 
    a 422 status code with a custom message describing the error.

    A JSON response with a 422 status code and a detailed error message 
    describing the validation issues. The response contains:
        - "detail": A simple message indicating a validation error.
        - "errors": A list of dictionaries containing information about the  
            validation errors, each with the following keys:
            - "field_name": The field that caused the error.
            - "error_msg": A description of the error.
            - "value_received": The value that was provided in the request.
            - "expected_type": The type of the value that was expected.
    """

    logger.error(f"Validation error occurred for request {request.method} {request.url}")
    logger.error(f"Request body: {await request.json()}")
    logger.error("Response status: 422")

    content = {
        "detail": "Validation error",
        "errors": [
            {
                "field_name": error["loc"][-1], 
                "error_msg": error["msg"],
                "value_received": error["input"],
                "expected_type": error["type"]
            }
            for error in exc.errors()
        ]
    }
    
    logger.error(f"Response payload: {content}")

    return JSONResponse(
        status_code=422,
        content=content
    )


# ---------- ENDPOINTS ----------


standard_responses = {
    500: {
        "model": ServerErrorResponse
    },
    422: {
        "model": ValidationErrorResponse
    },
    401: {
        "model": UnauthorizedErrorResponse
    }
}

tags = ["Endpoints"]


@app.get("/check", response_model=HealthCheck, responses=standard_responses, tags=tags)
async def check(
    request: Request, 
    _ = Depends(log_request), 
    creds: str = Depends(authenticate)
):
    """Check if the server is running."""

    try:
        response = {"status": "active"}

        logger.info("Response status: 200")
        logger.info(f"Response payload: {response}")

        return JSONResponse(
            status_code=200,
            content=response
        )
    
    except Exception as error:
        error_trace = traceback.format_exc()

        logger.error(f"Check failed.")
        logger.error(f"Error message: {str(error)}\n\n{error_trace}")
        logger.error("Response status: 500")

        raise HTTPException(
            status_code=500,
            detail="Internal server error occured."
        )


@app.post("/inference", response_model=ModelResponse, responses=standard_responses, tags=tags)
async def inference(
    payload: ModelRequest, 
    request: Request, 
    _ = Depends(log_request),
    creds: str = Depends(authenticate)
):
    """
    Model inference on input data. Inference can be performed on 
    multiple observations in a single request.
    """
    
    try:

        logger.info(f"Request payload: {payload.dict()}")

        request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # pass data to model
        logger.info("Passing payload to model...")
        data = payload.data.dict()
        preds = model.predict(data)

        # log request/response for monitoring
        logger.info("Capturing payload and model predictions...")
        data["prediction"] = preds
        data["identifier"] = payload.identifier
        data["request_time"] = request_time

        # collect data in separate thread
        data_collection_executor.submit(data_client.collect, data)

        logger.info("Returning predictions...")

        response = {
            "identifier": payload.identifier,
            "predictions": preds
        }

        logger.info(f"Response status: 200")
        logger.info(f"Response payload: {response}")

        return JSONResponse(
            status_code=200,
            content=response
        )
    
    except Exception as error:
        error_trace = traceback.format_exc()

        logger.error(f"Inference failed.")
        logger.error(f"Error message: {str(error)}\n\n{error_trace}")
        logger.error("Response status: 500")

        raise HTTPException(
            status_code=500,
            detail="Internal server error occured."
        )
