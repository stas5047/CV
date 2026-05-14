import pytest

from aerovision_worker.device import DeviceUnavailableError, select_device


def test_select_device_forces_cpu_without_cuda_probe() -> None:
    result = select_device("cpu", cuda_available=lambda: True)

    assert result.requested == "cpu"
    assert result.selected == "cpu"


def test_select_device_auto_uses_cuda_when_available() -> None:
    result = select_device("auto", cuda_available=lambda: True)

    assert result.requested == "auto"
    assert result.selected == "cuda"


def test_select_device_auto_falls_back_to_cpu_when_cuda_unavailable() -> None:
    result = select_device("auto", cuda_available=lambda: False)

    assert result.requested == "auto"
    assert result.selected == "cpu"


def test_select_device_cuda_fails_when_unavailable() -> None:
    with pytest.raises(DeviceUnavailableError, match="CUDA requested but unavailable"):
        select_device("cuda", cuda_available=lambda: False)
