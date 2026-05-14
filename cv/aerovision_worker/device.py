from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


class DeviceUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeviceSelection:
    requested: str
    selected: str


def torch_cuda_available() -> bool:
    try:
        import torch
    except Exception:
        return False
    return bool(torch.cuda.is_available())


def select_device(
    requested: str,
    *,
    cuda_available: Callable[[], bool] | None = None,
) -> DeviceSelection:
    probe = cuda_available or torch_cuda_available
    if requested == "cpu":
        return DeviceSelection(requested=requested, selected="cpu")
    if requested == "auto":
        return DeviceSelection(requested=requested, selected="cuda" if probe() else "cpu")
    if requested == "cuda":
        if not probe():
            raise DeviceUnavailableError("CUDA requested but unavailable")
        return DeviceSelection(requested=requested, selected="cuda")
    raise ValueError(f"Unsupported CV device: {requested}")
