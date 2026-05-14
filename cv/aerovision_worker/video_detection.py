from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from aerovision_worker.video_types import VideoDetection


def detections_from_result(
    result: Any,
    *,
    job_id: str,
    media_id: str,
    frame_index: int,
    timestamp_ms: int,
    frame_width: int,
    frame_height: int,
) -> list[VideoDetection]:
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return []
    xyxy = _array(getattr(boxes, "xyxy", []))
    confs = _array(getattr(boxes, "conf", []))
    classes = _array(getattr(boxes, "cls", []))
    ids = _array(getattr(boxes, "id", []))
    detections: list[VideoDetection] = []
    for index, box in enumerate(xyxy):
        x1, y1, x2, y2 = _clamp_box(box, frame_width=frame_width, frame_height=frame_height)
        if x2 <= x1 or y2 <= y1:
            continue
        detections.append(
            VideoDetection(
                job_id=job_id,
                media_id=media_id,
                frame_index=frame_index,
                timestamp_ms=timestamp_ms,
                class_id=int(classes[index]) if index < len(classes) else 0,
                class_name="drone",
                confidence=float(confs[index]) if index < len(confs) else 0.0,
                bbox_x1=x1,
                bbox_y1=y1,
                bbox_x2=x2,
                bbox_y2=y2,
                frame_width=frame_width,
                frame_height=frame_height,
                track_id=_track_id(ids, index),
            )
        )
    return detections


def annotated_frame(frame: np.ndarray, detections: list[VideoDetection]) -> np.ndarray:
    annotated = frame.copy()
    for detection in detections:
        p1 = (int(round(detection.bbox_x1)), int(round(detection.bbox_y1)))
        p2 = (int(round(detection.bbox_x2)), int(round(detection.bbox_y2)))
        cv2.rectangle(annotated, p1, p2, (0, 255, 0), 2)
        label = f"drone {detection.confidence:.2f}"
        if detection.track_id is not None:
            label = f"{label} #{detection.track_id}"
        cv2.putText(
            annotated,
            label,
            (p1[0], max(12, p1[1] - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )
    return annotated


def _array(value: Any) -> np.ndarray:
    if value is None:
        return np.asarray([])
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value)


def _track_id(ids: np.ndarray, index: int) -> int | None:
    if not ids.size or index >= len(ids) or np.isnan(ids[index]):
        return None
    return int(ids[index])


def _clamp_box(
    box: Any,
    *,
    frame_width: int,
    frame_height: int,
) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = [float(value) for value in box[:4]]
    return (
        max(0.0, min(float(frame_width), x1)),
        max(0.0, min(float(frame_height), y1)),
        max(0.0, min(float(frame_width), x2)),
        max(0.0, min(float(frame_height), y2)),
    )
