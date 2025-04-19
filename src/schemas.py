from typing import List, Literal, Any

from pydantic import BaseModel


class ModelFeatures(BaseModel):
    """Model features."""

    class Config:
        extra = "forbid"

    mean_radius: List[float]
    mean_texture: List[float]
    mean_perimeter: List[float]
    mean_area: List[float]
    mean_smoothness: List[float]
    mean_compactness: List[float]
    mean_concavity: List[float]
    mean_concave_points: List[float]
    mean_symmetry: List[float]
    mean_fractal_dimension: List[float]


class ModelRequest(BaseModel):
    """Base API request."""

    class Config:
        extra = "forbid"

    identifier: List[str]
    data: ModelFeatures


class ModelResponse(BaseModel):
    """Base model response."""

    identifier: List[str]
    predictions: List[float]


class HealthCheck(BaseModel):
    """Health check response."""

    status: Literal["active"]


class ValidationErrorDetail(BaseModel):
    """Validation error object."""

    field_name: str
    error_message: str
    value_received: Any
    expected_type: Any


class ValidationErrorResponse(BaseModel):
    """Custom format for validation error responses."""

    detail: Literal["Validation error"]
    errors: List[ValidationErrorDetail]


class UnauthorizedErrorResponse(BaseModel):
    """Custom unauthorized error response."""

    detail: Literal["Invalid credentials."]


class ServerErrorResponse(BaseModel):
    """Custom server error response."""

    detail: Literal["Internal server error occured."]
    