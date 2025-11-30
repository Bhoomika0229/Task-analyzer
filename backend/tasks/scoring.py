from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Dict, Any, Tuple, Set, Optional


# ---- Configuration ----

SMART_WEIGHTS = {
    "importance": 0.4,
    "urgency": 0.3,
    "effort": 0.2,
    "dependencies": 0.1,
}

FASTEST_WINS_WEIGHT_EFFORT = 0.7
FASTEST_WINS_WEIGHT_URGENCY = 0.2
FASTEST_WINS_WEIGHT_IMPORTANCE = 0.1

DEADLINE_DRIVEN_WEIGHT_URGENCY = 0.7
DEADLINE_DRIVEN_WEIGHT_IMPORTANCE = 0.3

HIGH_IMPACT_WEIGHT_IMPORTANCE = 1.0


# ---- Helper functions ----

def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def safe_days_until_due(d: Optional[date]) -> Optional[int]:
    if not d:
        return None
    today = date.today()
    return (d - today).days


def compute_urgency_score(due: Optional[date]) -> Tuple[float, str]:
    """
    Map days until due into 0–10 urgency.
    Overdue tasks (negative days) are capped.
    """
    days = safe_days_until_due(due)
    if days is None:
        # Neutral urgency for missing date
        return 5.0, "neutral urgency (no due date)"

    # Past due: more urgent than due very soon
    if days < 0:
        # Cap at -7 days to avoid runaway scores
        days_capped = max(days, -7)
        urgency = clamp(10 + days_capped, 7, 10)  # 1 week overdue → ~9
        return urgency, f"overdue by {-days} days"

    # 0 days → 10, 10+ days → 0
    raw = 10 - days
    urgency = clamp(raw, 0, 10)
    if days == 0:
        reason = "due today"
    elif days <= 3:
        reason = f"due soon (in {days} days)"
    else:
        reason = f"due in {days} days"
    return urgency, reason


def compute_effort_score(hours: Optional[float]) -> Tuple[float, str]:
    """
    Higher score for lower effort (quick wins).
    Returns (score, description).
    """
    if hours is None or hours <= 0:
        return 6.0, "unknown effort (assumed medium)"

    if hours <= 1:
        return 10.0, f"very low effort (~{hours}h)"
    if hours <= 3:
        return 8.0, f"low effort (~{hours}h)"
    if hours <= 6:
        return 6.0, f"medium effort (~{hours}h)"
    if hours <= 10:
        return 4.0, f"high effort (~{hours}h)"
    return 2.0, f"very high effort (~{hours}h)"


def normalize_importance(importance: Any) -> int:
    try:
        value = int(importance)
    except (TypeError, ValueError):
        return 5
    return int(clamp(value, 1, 10))


def build_dependency_graph(tasks: List[Dict[str, Any]]) -> Tuple[Dict[str, List[str]], Dict[str, int]]:
    """
    Returns adjacency list (task -> its dependencies) and reverse count (task -> how many depend on it).
    If tasks have no 'id', a fallback index-based id is used.
    """
    id_to_deps: Dict[str, List[str]] = {}
    dependents_count: Dict[str, int] = {}

    # First assign ids
    for idx, task in enumerate(tasks):
        task_id = task.get("id") or str(idx)
        task["_internal_id"] = task_id
        id_to_deps[task_id] = []
        dependents_count[task_id] = 0

    # Fill deps and reverse counts
    for task in tasks:
        task_id = task["_internal_id"]
        deps = task.get("dependencies") or []
        norm_deps = [str(d) for d in deps]
        id_to_deps[task_id] = norm_deps
        for d in norm_deps:
            if d not in dependents_count:
                dependents_count[d] = 0
            dependents_count[d] += 1

    return id_to_deps, dependents_count


def detect_cycles(graph: Dict[str, List[str]]) -> Set[str]:
    """
    Basic DFS-based cycle detection.
    Returns a set of task ids that are part of any cycle.
    """
    visited: Set[str] = set()
    on_stack: Set[str] = set()
    in_cycle: Set[str] = set()

    def dfs(node: str):
        if node in visited:
            return
        visited.add(node)
        on_stack.add(node)
        for neigh in graph.get(node, []):
            if neigh not in visited:
                dfs(neigh)
            elif neigh in on_stack:
                # Mark cycle nodes (approximate: mark current and neighbor)
                in_cycle.add(node)
                in_cycle.add(neigh)
        on_stack.remove(node)

    for node in graph.keys():
        if node not in visited:
            dfs(node)

    return in_cycle


# ---- Strategy scoring functions ----

def score_fastest_wins(importance: float, urgency: float, effort: float) -> float:
    # Effort already represents "quick win" as higher for lower hours
    return (
        FASTEST_WINS_WEIGHT_EFFORT * effort
        + FASTEST_WINS_WEIGHT_URGENCY * urgency
        + FASTEST_WINS_WEIGHT_IMPORTANCE * importance
    )


def score_deadline_driven(importance: float, urgency: float) -> float:
    return (
        DEADLINE_DRIVEN_WEIGHT_URGENCY * urgency
        + DEADLINE_DRIVEN_WEIGHT_IMPORTANCE * importance
    )


def score_high_impact(importance: float) -> float:
    return HIGH_IMPACT_WEIGHT_IMPORTANCE * importance


def score_smart_balance(
    importance: float,
    urgency: float,
    effort: float,
    blocks: int,
    weights: Dict[str, float] = None,
) -> float:
    w = weights or SMART_WEIGHTS
    return (
        w.get("importance", 0.0) * importance
        + w.get("urgency", 0.0) * urgency
        + w.get("effort", 0.0) * effort
        + w.get("dependencies", 0.0) * float(blocks)
    )


# ---- Public API ----

@dataclass
class ScoredTask:
    task: Dict[str, Any]
    score: float
    strategy: str
    explanation: str
    has_cycle: bool = False


def score_task(
    task: Dict[str, Any],
    strategy: str,
    dependents_count: Dict[str, int],
    weights: Dict[str, float] | None = None,
    in_cycle: Optional[Set[str]] = None,
) -> ScoredTask:
    """
    Compute score and explanation for a single task under a given strategy.
    """
    task_id = task.get("_internal_id")
    importance = float(normalize_importance(task.get("importance")))
    due_date = task.get("due_date")
    hours = task.get("estimated_hours")

    urgency, urgency_reason = compute_urgency_score(due_date)
    effort, effort_reason = compute_effort_score(hours)
    blocks = dependents_count.get(task_id, 0)

    explanation_bits = []

    if strategy == "fastest_wins":
        score = score_fastest_wins(importance, urgency, effort)
        explanation_bits.append("prioritized quick wins (low effort)")
    elif strategy == "high_impact":
        score = score_high_impact(importance)
        explanation_bits.append("prioritized high importance")
    elif strategy == "deadline_driven":
        score = score_deadline_driven(importance, urgency)
        explanation_bits.append("prioritized close deadlines")
    else:  # smart_balance (default)
        score = score_smart_balance(importance, urgency, effort, blocks, weights)
        explanation_bits.append("balanced importance, urgency, effort, and dependencies")

    # Add factor-specific explanations
    explanation_bits.append(f"importance {importance}/10")
    explanation_bits.append(f"urgency because it is {urgency_reason}")
    explanation_bits.append(effort_reason)
    if blocks > 0:
        explanation_bits.append(f"unblocks {blocks} other task(s)")

    cycle_flag = False
    if in_cycle and task_id in in_cycle:
        cycle_flag = True
        explanation_bits.append("involved in a circular dependency")

    explanation = "; ".join(explanation_bits)

    return ScoredTask(
        task=task,
        score=round(score, 2),
        strategy=strategy,
        explanation=explanation,
        has_cycle=cycle_flag,
    )


def analyze_tasks(
    tasks: List[Dict[str, Any]],
    strategy: str = "smart_balance",
    weights: Dict[str, float] | None = None,
) -> List[Dict[str, Any]]:
    """
    Main entry point: scores and sorts tasks.
    Returns list of task dicts augmented with score and explanation.
    """
    if not tasks:
        return []

    # Build dependency info
    graph, dependents = build_dependency_graph(tasks)
    cycle_nodes = detect_cycles(graph)

    scored: List[ScoredTask] = []
    for task in tasks:
        scored_task = score_task(
            task,
            strategy=strategy,
            dependents_count=dependents,
            weights=weights,
            in_cycle=cycle_nodes,
        )
        scored.append(scored_task)

    # Sort by score desc, then by importance desc for stability
    scored.sort(key=lambda st: (st.score, st.task.get("importance", 0)), reverse=True)

    # Return plain dicts for JSON
    result: List[Dict[str, Any]] = []
    for st in scored:
        t = dict(st.task)  # shallow copy
        t.pop("_internal_id", None)
        t["score"] = st.score
        t["strategy_used"] = st.strategy
        t["explanation"] = st.explanation
        t["has_cycle"] = st.has_cycle
        result.append(t)

    return result


def suggest_top_tasks(
    tasks: List[Dict[str, Any]],
    strategy: str = "smart_balance",
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """
    Convenience helper to get top-N tasks with scores.
    """
    analyzed = analyze_tasks(tasks, strategy=strategy)
    return analyzed[:limit]
