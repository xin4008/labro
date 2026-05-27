import json
import os
import uuid
import shutil
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _safe_dir(name):
    """Sanitize a string for use as a directory name."""
    return "".join(c for c in name if c.isalnum() or c in "._- ").strip()[:80]


def list_experiments():
    """Return list of experiment summaries sorted by created_at desc."""
    if not os.path.isdir(DATA_DIR):
        return []
    result = []
    for d in sorted(os.listdir(DATA_DIR), reverse=True):
        exp_path = os.path.join(DATA_DIR, d)
        json_path = os.path.join(exp_path, "experiment.json")
        if not os.path.isfile(json_path):
            continue
        with open(json_path, "r", encoding="utf-8") as f:
            exp = json.load(f)
        total = len(exp["steps"])
        done = sum(1 for s in exp["steps"] if s["completed"])
        result.append({
            "id": exp["id"],
            "title": exp["title"],
            "created_at": exp["created_at"],
            "total_steps": total,
            "completed_steps": done,
        })
    return result


def get_experiment(exp_id):
    """Load a single experiment by ID."""
    exp_dir = _find_experiment_dir(exp_id)
    if not exp_dir:
        return None
    json_path = os.path.join(exp_dir, "experiment.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_experiment(title, objective, references):
    """Create a new experiment with no steps yet."""
    exp_id = uuid.uuid4().hex[:12]
    today = date.today().isoformat()
    dir_name = f"{_safe_dir(title)}_{today}_{exp_id}"
    exp_dir = os.path.join(DATA_DIR, dir_name)
    os.makedirs(os.path.join(exp_dir, "photos"), exist_ok=True)

    experiment = {
        "id": exp_id,
        "title": title,
        "objective": objective,
        "references": references,
        "created_at": today,
        "updated_at": today,
        "steps": [],
    }
    with open(os.path.join(exp_dir, "experiment.json"), "w", encoding="utf-8") as f:
        json.dump(experiment, f, ensure_ascii=False, indent=2)
    return experiment


def update_experiment(exp_id, experiment):
    """Save updated experiment data to disk."""
    exp_dir = _find_experiment_dir(exp_id)
    if not exp_dir:
        raise FileNotFoundError(f"Experiment {exp_id} not found")
    json_path = os.path.join(exp_dir, "experiment.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(experiment, f, ensure_ascii=False, indent=2)


def delete_experiment(exp_id):
    """Delete an experiment and all its data."""
    exp_dir = _find_experiment_dir(exp_id)
    if exp_dir:
        shutil.rmtree(exp_dir)


def save_photo(exp_id, step_id, file_storage):
    """Save an uploaded photo and return its relative path."""
    exp_dir = _find_experiment_dir(exp_id)
    if not exp_dir:
        raise FileNotFoundError(f"Experiment {exp_id} not found")
    photos_dir = os.path.join(exp_dir, "photos")
    os.makedirs(photos_dir, exist_ok=True)

    import time
    ext = os.path.splitext(file_storage.filename)[1] or ".jpg"
    safe_name = f"step{step_id}_{int(time.time()*1000)}{ext}"
    filepath = os.path.join(photos_dir, safe_name)
    file_storage.save(filepath)
    return f"photos/{safe_name}"


def _find_experiment_dir(exp_id):
    """Find experiment directory by experiment ID."""
    if not os.path.isdir(DATA_DIR):
        return None
    for d in os.listdir(DATA_DIR):
        if d.endswith(f"_{exp_id}"):
            full = os.path.join(DATA_DIR, d)
            if os.path.isdir(full):
                return full
    return None
