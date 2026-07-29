from .api import create_app
from .backend import (
    BackendConnectionError,
    BackendError,
    BackendGenerationError,
    BackendIdentity,
    BackendIdentityError,
    BackendMessage,
    BackendOutOfMemoryError,
    BackendReadiness,
    BackendRequestError,
    BackendTimeoutError,
    GenerationBackend,
    GenerationChunk,
    GenerationHandle,
    GenerationRequest,
)
from .profiles import (
    ModelServingProfile,
    ModelServingProfiles,
    ProfileValidationError,
    load_profiles,
)

__all__ = [
    "BackendConnectionError",
    "BackendError",
    "BackendGenerationError",
    "BackendIdentity",
    "BackendIdentityError",
    "BackendMessage",
    "BackendOutOfMemoryError",
    "BackendReadiness",
    "BackendRequestError",
    "BackendTimeoutError",
    "GenerationBackend",
    "GenerationChunk",
    "GenerationHandle",
    "GenerationRequest",
    "ModelServingProfile",
    "ModelServingProfiles",
    "ProfileValidationError",
    "create_app",
    "load_profiles",
    "TransformersGenerationBackend",
]


def __getattr__(name: str):
    if name == "TransformersGenerationBackend":
        from .transformers_backend import TransformersGenerationBackend

        return TransformersGenerationBackend
    raise AttributeError(name)
