"""
Multi-Criteria Decision Support System (MCDSS)
===============================================
A weighted scoring model to rank alternatives across multiple criteria.

Usage:
    python mcdss.py

Or import and use programmatically:
    from mcdss import MCDSS
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class Criterion:
    name: str
    weight: float  # importance weight (any positive number; normalized internally)
    description: str = ""

    def __post_init__(self):
        if self.weight <= 0:
            raise ValueError(f"Weight for '{self.name}' must be positive.")


@dataclass
class Alternative:
    name: str
    scores: dict[str, float] = field(default_factory=dict)  # {criterion_name: raw_score}
    description: str = ""

    def set_score(self, criterion_name: str, score: float) -> None:
        if not (0.0 <= score <= 10.0):
            raise ValueError(f"Score must be between 0 and 10, got {score}.")
        self.scores[criterion_name] = score


@dataclass
class Result:
    alternative: Alternative
    weighted_score: float       # raw weighted total
    normalized_score: float     # 0–100 percentage
    rank: int
    breakdown: dict[str, float] = field(default_factory=dict)  # per-criterion contribution


# ── Core engine ───────────────────────────────────────────────────────────────

class MCDSS:
    """
    Multi-Criteria Decision Support System.

    Steps:
        1. Add criteria with weights.
        2. Add alternatives.
        3. Set scores (0–10) for each alternative on each criterion.
        4. Call evaluate() to get ranked results.
    """

    def __init__(self, name: str = "Decision Analysis"):
        self.name = name
        self.criteria: list[Criterion] = []
        self.alternatives: list[Alternative] = []

    # ── Setup ────────────────────────────────────────────────────────────────

    def add_criterion(self, name: str, weight: float, description: str = "") -> Criterion:
        if any(c.name == name for c in self.criteria):
            raise ValueError(f"Criterion '{name}' already exists.")
        c = Criterion(name=name, weight=weight, description=description)
        self.criteria.append(c)
        return c

    def add_alternative(self, name: str, description: str = "") -> Alternative:
        if any(a.name == name for a in self.alternatives):
            raise ValueError(f"Alternative '{name}' already exists.")
        a = Alternative(name=name, description=description)
        self.alternatives.append(a)
        return a

    def set_score(self, alternative_name: str, criterion_name: str, score: float) -> None:
        alt = self._get_alternative(alternative_name)
        self._get_criterion(criterion_name)   # validates existence
        alt.set_score(criterion_name, score)

    # ── Evaluation ───────────────────────────────────────────────────────────

    def evaluate(self) -> list[Result]:
        """
        Compute weighted scores and return a ranked list of Results.
        Uses simple additive weighting (SAW / WSM).
        """
        self._validate()

        total_weight = sum(c.weight for c in self.criteria)
        # Max possible score if every alternative scored 10 on every criterion
        max_possible = 10.0 * total_weight

        raw_results: list[Result] = []

        for alt in self.alternatives:
            weighted_total = 0.0
            breakdown: dict[str, float] = {}

            for crit in self.criteria:
                raw = alt.scores.get(crit.name, 0.0)
                contribution = raw * crit.weight
                breakdown[crit.name] = contribution
                weighted_total += contribution

            normalized = (weighted_total / max_possible) * 100 if max_possible else 0.0

            raw_results.append(Result(
                alternative=alt,
                weighted_score=weighted_total,
                normalized_score=round(normalized, 2),
                rank=0,
                breakdown=breakdown,
            ))

        # Rank by normalized score (descending)
        raw_results.sort(key=lambda r: r.normalized_score, reverse=True)
        for i, r in enumerate(raw_results):
            r.rank = i + 1

        return raw_results

    # ── Sensitivity analysis ──────────────────────────────────────────────────

    def sensitivity_analysis(self, criterion_name: str, steps: int = 5) -> list[dict]:
        """
        Vary the weight of one criterion across its range and show how rankings change.
        Returns a list of dicts: {weight, rankings: [(rank, alt_name, score), ...]}
        """
        self._get_criterion(criterion_name)
        original = {c.name: c.weight for c in self.criteria}
        output = []

        weight_values = [i * (10 / (steps - 1)) for i in range(steps)]
        for w in weight_values:
            self._get_criterion(criterion_name).weight = max(0.01, w)
            results = self.evaluate()
            output.append({
                "weight": round(w, 2),
                "rankings": [(r.rank, r.alternative.name, r.normalized_score) for r in results],
            })

        # Restore original weights
        for c in self.criteria:
            c.weight = original[c.name]

        return output

    # ── I/O ──────────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "criteria": [{"name": c.name, "weight": c.weight, "description": c.description}
                         for c in self.criteria],
            "alternatives": [{"name": a.name, "description": a.description, "scores": a.scores}
                              for a in self.alternatives],
        }

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Saved to {path}")

    @classmethod
    def load(cls, path: str) -> "MCDSS":
        with open(path) as f:
            data = json.load(f)
        m = cls(name=data.get("name", "Decision Analysis"))
        for c in data["criteria"]:
            m.add_criterion(c["name"], c["weight"], c.get("description", ""))
        for a in data["alternatives"]:
            alt = m.add_alternative(a["name"], a.get("description", ""))
            for crit_name, score in a.get("scores", {}).items():
                alt.set_score(crit_name, score)
        return m

    # ── Display ──────────────────────────────────────────────────────────────

    def print_results(self, results: Optional[list[Result]] = None) -> None:
        if results is None:
            results = self.evaluate()

        total_weight = sum(c.weight for c in self.criteria)

        print(f"\n{'═' * 60}")
        print(f"  {self.name}")
        print(f"{'═' * 60}")

        # Criteria table
        print("\n  CRITERIA")
        print(f"  {'Name':<20} {'Weight':>8}  {'Normalized %':>13}")
        print(f"  {'-'*20} {'-'*8}  {'-'*13}")
        for c in self.criteria:
            pct = (c.weight / total_weight) * 100
            print(f"  {c.name:<20} {c.weight:>8.1f}  {pct:>12.1f}%")

        # Results table
        print(f"\n  RANKING")
        crit_cols = "  ".join(f"{c.name[:10]:>12}" for c in self.criteria)
        print(f"  {'Rank':<5} {'Alternative':<18} {crit_cols}  {'Score':>7}")
        print(f"  {'-'*5} {'-'*18} {'  '.join(['-'*12]*len(self.criteria))}  {'-'*7}")

        for r in results:
            crit_vals = "  ".join(
                f"{r.alternative.scores.get(c.name, 0):>12.1f}"
                for c in self.criteria
            )
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(r.rank, f"#{r.rank} ")
            print(f"  {medal:<5} {r.alternative.name:<18} {crit_vals}  {r.normalized_score:>6.1f}%")

        print(f"\n  ✔  Best choice: {results[0].alternative.name}  ({results[0].normalized_score:.1f}%)\n")

    def print_sensitivity(self, criterion_name: str) -> None:
        rows = self.sensitivity_analysis(criterion_name)
        print(f"\n  Sensitivity — '{criterion_name}' weight vs. rankings\n")
        print(f"  {'Weight':>8}  Rankings (best → worst)")
        print(f"  {'-'*8}  {'-'*40}")
        for row in rows:
            ranking_str = " > ".join(name for _, name, _ in row["rankings"])
            print(f"  {row['weight']:>8.1f}  {ranking_str}")
        print()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_criterion(self, name: str) -> Criterion:
        for c in self.criteria:
            if c.name == name:
                return c
        raise KeyError(f"Criterion '{name}' not found.")

    def _get_alternative(self, name: str) -> Alternative:
        for a in self.alternatives:
            if a.name == name:
                return a
        raise KeyError(f"Alternative '{name}' not found.")

    def _validate(self) -> None:
        if not self.criteria:
            raise ValueError("Add at least one criterion before evaluating.")
        if not self.alternatives:
            raise ValueError("Add at least one alternative before evaluating.")


# ── Interactive CLI ───────────────────────────────────────────────────────────

def interactive_session() -> None:
    print("\n╔══════════════════════════════════════╗")
    print("║  Multi-Criteria Decision Support     ║")
    print("╚══════════════════════════════════════╝")

    name = input("\nDecision title (press Enter to skip): ").strip() or "My Decision"
    m = MCDSS(name=name)

    # --- Criteria ---
    print("\n── Step 1: Define criteria ──")
    print("Enter each criterion with a weight (1–10). Blank name to finish.\n")
    while True:
        cname = input("  Criterion name: ").strip()
        if not cname:
            if not m.criteria:
                print("  (Need at least one criterion)")
                continue
            break
        try:
            w = float(input(f"  Weight for '{cname}' (1–10): "))
            m.add_criterion(cname, w)
            print(f"  ✔ Added '{cname}' (weight={w})\n")
        except (ValueError, Exception) as e:
            print(f"  ✘ {e}\n")

    # --- Alternatives ---
    print("\n── Step 2: Define alternatives ──")
    print("Enter each alternative. Blank name to finish.\n")
    while True:
        aname = input("  Alternative name: ").strip()
        if not aname:
            if not m.alternatives:
                print("  (Need at least one alternative)")
                continue
            break
        m.add_alternative(aname)
        print(f"  ✔ Added '{aname}'\n")

    # --- Scores ---
    print("\n── Step 3: Score each alternative (0–10) ──\n")
    for alt in m.alternatives:
        print(f"  Scores for '{alt.name}':")
        for crit in m.criteria:
            while True:
                try:
                    s = float(input(f"    {crit.name}: "))
                    alt.set_score(crit.name, s)
                    break
                except ValueError as e:
                    print(f"    ✘ {e}")

    # --- Results ---
    results = m.evaluate()
    m.print_results(results)

    # --- Optional sensitivity ---
    do_sens = input("  Run sensitivity analysis? (y/n): ").strip().lower()
    if do_sens == "y" and len(m.criteria) > 1:
        print("  Criteria: " + ", ".join(c.name for c in m.criteria))
        cname = input("  Criterion to vary: ").strip()
        try:
            m.print_sensitivity(cname)
        except KeyError as e:
            print(f"  ✘ {e}")

    # --- Save ---
    do_save = input("  Save to JSON? (y/n): ").strip().lower()
    if do_save == "y":
        path = input("  File path (e.g. decision.json): ").strip() or "decision.json"
        m.save(path)


# ── Demo (runs when executed directly) ───────────────────────────────────────

def demo() -> None:
    """Pre-built example: choosing a software framework."""
    m = MCDSS("Software Framework Selection")

    m.add_criterion("Performance",    weight=8,  description="Runtime speed and throughput")
    m.add_criterion("Ecosystem",      weight=7,  description="Libraries, community, support")
    m.add_criterion("Learning Curve", weight=5,  description="Ease of onboarding (lower = harder)")
    m.add_criterion("Scalability",    weight=9,  description="Ability to handle growth")
    m.add_criterion("Cost",           weight=6,  description="Licensing and infra cost")

    frameworks = {
        "Django":   [7, 9, 7, 7, 9],
        "FastAPI":  [9, 7, 6, 8, 9],
        "Express":  [8, 9, 8, 7, 9],
        "Spring":   [8, 8, 4, 9, 6],
        "Rails":    [6, 8, 8, 6, 8],
    }

    for fname, scores in frameworks.items():
        m.add_alternative(fname)
        for crit, score in zip(m.criteria, scores):
            m.set_score(fname, crit.name, score)

    results = m.evaluate()
    m.print_results(results)
    m.print_sensitivity("Scalability")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--load":
        path = sys.argv[2] if len(sys.argv) > 2 else "decision.json"
        m = MCDSS.load(path)
        m.print_results()
    else:
        # Ask user: demo or interactive
        print("\nMCDSS — Multi-Criteria Decision Support System")
        print("  1. Run built-in demo")
        print("  2. Interactive session")
        choice = input("\nChoose (1/2): ").strip()
        if choice == "1":
            demo()
        else:
            interactive_session()
