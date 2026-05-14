from __future__ import annotations

from pathlib import Path

from aerovision_training.notebook_checks import check_notebook_template


def test_yolo26n_notebook_uses_pretrained_weights_not_scratch() -> None:
    check_notebook_template(Path("training/notebooks/yolo26n_finetune_template.ipynb"), "yolo26n.pt")


def test_yolo26s_notebook_uses_pretrained_weights_not_scratch() -> None:
    check_notebook_template(Path("training/notebooks/yolo26s_finetune_template.ipynb"), "yolo26s.pt")
