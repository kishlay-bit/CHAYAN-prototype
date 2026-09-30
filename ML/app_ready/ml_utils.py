import io
import hashlib
import random
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageFilter, ImageStat

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

SIMULATION_MODE = True          # False once real weights are loaded
MODEL_VERSION = "onion-yolov8-v0.3-sim"
CONFIDENCE_THRESHOLD = 0.55

DEFECT_CLASSES = ["good", "damaged", "rotten", "sprouted", "undersized"]

# Grading thresholds (per PS 26031 guidance draft)
GRADE_A_MIN_SCORE = 70


# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------

@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int
    label: str
    confidence: float


@dataclass
class QualityCheckResult:
    passed: bool
    brightness: float
    sharpness: float
    issues: List[str] = field(default_factory=list)


@dataclass
class GradingResult:
    score: int
    grade: str
    composition: dict
    boxes: List[BoundingBox]
    total_onions: int
    model_version: str


# --------------------------------------------------------------------------
# Image quality checks (REAL — these actually run on the image)
# --------------------------------------------------------------------------

def check_image_quality(image: Image.Image) -> QualityCheckResult:
    """
    Basic pre-inference quality gate. Rejects images that would make
    downstream detection unreliable: too dark, too bright, or blurry.
    """
    gray = image.convert("L")

    # Brightness: mean pixel intensity (0-255)
    stat = ImageStat.Stat(gray)
    brightness = stat.mean[0]

    # Sharpness: variance of a Laplacian-like edge filter as a blur proxy
    edges = gray.filter(ImageFilter.FIND_EDGES)
    sharpness = float(np.var(np.asarray(edges, dtype=np.float32)))

    issues = []
    if brightness < 60:
        issues.append("low_light")
    if brightness > 200:
        issues.append("overexposed")
    if sharpness < 120:
        issues.append("blurry")

    return QualityCheckResult(
        passed=len(issues) == 0,
        brightness=round(brightness, 2),
        sharpness=round(sharpness, 2),
        issues=issues,
    )


# --------------------------------------------------------------------------
# Detection + classification (SIMULATED — deterministic per image)
# --------------------------------------------------------------------------

def _seed_from_image(image: Image.Image) -> int:
    """Derive a stable seed from image bytes so the same photo always
    produces the same simulated result (useful for demo repeatability)."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    digest = hashlib.sha256(buf.getvalue()).hexdigest()
    return int(digest[:8], 16)


def detect_onions(image: Image.Image) -> List[BoundingBox]:
    """
    Runs onion instance detection on the input image.

    SIMULATION_MODE: generates plausible, image-seeded bounding boxes
    instead of calling a real detector. Replace this function body with:

        results = yolo_model.predict(image, conf=CONFIDENCE_THRESHOLD)
        return _parse_yolo_output(results)

    once model weights are available.
    """
    rng = random.Random(_seed_from_image(image))
    w, h = image.size
    n_onions = rng.randint(14, 22)

    boxes = []
    for _ in range(n_onions):
        box_w = rng.randint(int(w * 0.06), int(w * 0.10))
        box_h = box_w + rng.randint(-4, 4)
        x = rng.randint(0, max(1, w - box_w))
        y = rng.randint(0, max(1, h - box_h))
        label = rng.choices(
            DEFECT_CLASSES,
            weights=[72, 8, 4, 3, 3],  # roughly matches expected field distribution
            k=1,
        )[0]
        confidence = round(rng.uniform(CONFIDENCE_THRESHOLD, 0.98), 3)
        boxes.append(BoundingBox(x, y, box_w, box_h, label, confidence))

    return boxes


def classify_defects(boxes: List[BoundingBox]) -> dict:
    """
    Aggregates per-box labels into lot-level composition percentages.
    In production this would consume the classifier head's softmax
    outputs directly instead of pre-assigned labels.
    """
    total = len(boxes)
    if total == 0:
        return {c: 0 for c in DEFECT_CLASSES}

    counts = {c: 0 for c in DEFECT_CLASSES}
    for box in boxes:
        counts[box.label] += 1

    composition = {
        c: round((counts[c] / total) * 100)
        for c in DEFECT_CLASSES
    }

    # correct rounding drift so percentages sum to exactly 100
    drift = 100 - sum(composition.values())
    if drift != 0:
        largest = max(composition, key=composition.get)
        composition[largest] += drift

    return composition


def compute_score(composition: dict) -> int:
    """
    Weighted quality score out of 100. Good onions contribute fully;
    each defect type is penalised by severity.
    """
    weights = {
        "good": 1.0,
        "damaged": 0.4,
        "rotten": 0.0,
        "sprouted": 0.3,
        "undersized": 0.5,
    }
    score = sum(composition.get(c, 0) * weights.get(c, 0) for c in DEFECT_CLASSES)
    return int(round(min(score, 100)))


def assign_grade(score: int) -> str:
    return "Grade A" if score >= GRADE_A_MIN_SCORE else "URS"


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def grade_onion_sample(image: Image.Image) -> Tuple[QualityCheckResult, GradingResult]:
    """
    Full pipeline entry point used by the API layer: quality gate ->
    detection -> classification -> scoring.
    """
    quality = check_image_quality(image)
    if not quality.passed:
        return quality, None

    boxes = detect_onions(image)
    composition = classify_defects(boxes)
    # "good" onions map to Grade A composition bucket downstream in the API layer
    score = compute_score(composition)
    grade = assign_grade(score)

    result = GradingResult(
        score=score,
        grade=grade,
        composition=composition,
        boxes=boxes,
        total_onions=len(boxes),
        model_version=MODEL_VERSION,
    )
    return quality, result