import os
import json
import glob
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Problems directory: /home/pandeyps/Prefix/rictrlab/problems
PROBLEMS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "problems")
# Also try alternative absolute path
ALT_PROBLEMS_DIR = "/home/pandeyps/Prefix/rictrlab/problems"
if os.path.exists(ALT_PROBLEMS_DIR):
    PROBLEMS_DIR = ALT_PROBLEMS_DIR

class Problem:
    def __init__(self, meta: dict, prompt_md: str, starter_code: str, tests_path: str, problem_dir: str):
        self.id = meta.get("id")
        self.slug = meta.get("slug")
        self.title = meta.get("title")
        self.difficulty = meta.get("difficulty")
        self.category = meta.get("category")
        self.description_short = meta.get("description_short", "")
        self.function_name = meta.get("function_name", "solve")
        self.prompt_md = prompt_md
        self.starter_code = starter_code
        self.tests_path = tests_path
        self.problem_dir = problem_dir
        self.meta = meta

    def to_short_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "difficulty": self.difficulty,
            "category": self.category,
            "description_short": self.description_short,
        }

    def to_detail_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "difficulty": self.difficulty,
            "category": self.category,
            "description_short": self.description_short,
            "prompt_md": self.prompt_md,
            "starter_code": self.starter_code,
            "function_name": self.function_name,
        }

# Global cache
_problems: Dict[str, Problem] = {}

def load_problems(force_reload: bool = False) -> Dict[str, Problem]:
    global _problems
    if _problems and not force_reload:
        return _problems

    _problems = {}
    if not os.path.exists(PROBLEMS_DIR):
        logger.warning(f"Problems directory not found: {PROBLEMS_DIR}")
        return _problems

    pattern = os.path.join(PROBLEMS_DIR, "*", "problem.json")
    files = glob.glob(pattern)
    logger.info(f"Scanning problems in {PROBLEMS_DIR}, found {len(files)} problem.json")

    for json_path in files:
        problem_dir = os.path.dirname(json_path)
        slug_dir = os.path.basename(problem_dir)
        try:
            with open(json_path, "r") as f:
                meta = json.load(f)
            slug = meta.get("slug", slug_dir)

            # Load prompt.md
            prompt_path = os.path.join(problem_dir, "prompt.md")
            prompt_md = ""
            if os.path.exists(prompt_path):
                with open(prompt_path, "r") as f:
                    prompt_md = f.read()
            else:
                logger.warning(f"prompt.md missing for {slug}")

            # Load starter.py
            starter_path = os.path.join(problem_dir, "starter.py")
            starter_code = ""
            if os.path.exists(starter_path):
                with open(starter_path, "r") as f:
                    starter_code = f.read()
            else:
                logger.warning(f"starter.py missing for {slug}")

            # Tests path
            tests_path = os.path.join(problem_dir, "tests.py")
            if not os.path.exists(tests_path):
                logger.warning(f"tests.py missing for {slug}, skipping")
                continue

            prob = Problem(meta, prompt_md, starter_code, tests_path, problem_dir)
            _problems[slug] = prob
            logger.info(f"Loaded problem: {slug} ({prob.title})")
        except Exception as e:
            logger.exception(f"Failed to load problem from {json_path}: {e}")

    return _problems

def get_problem(slug: str) -> Optional[Problem]:
    if not _problems:
        load_problems()
    return _problems.get(slug)

def list_problems() -> List[Problem]:
    if not _problems:
        load_problems()
    # Sort by id
    return sorted(_problems.values(), key=lambda p: p.id if isinstance(p.id, int) else 999)

def reload_problems():
    return load_problems(force_reload=True)

# Load on import
try:
    load_problems()
except Exception as e:
    logger.exception(f"Initial problem load failed: {e}")
