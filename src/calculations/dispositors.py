"""
Classical sign-dispositor chains for natal planets and lunar nodes.
"""

try:
    from .house_analysis import SIGN_RULERS
except ImportError:
    from house_analysis import SIGN_RULERS


def analyze_dispositors(chart: dict) -> dict:
    """Return direct dispositors, terminal dispositors, and detected cycles."""
    chains = {
        planet: _trace_chain(planet, chart)
        for planet in chart["planets"]
    }
    final_dispositors = sorted({
        chain["terminal_dispositor"]
        for chain in chains.values()
        if chain["terminal_type"] == "final_dispositor"
    })
    cycles = []
    seen_cycles = set()

    for chain in chains.values():
        if chain["terminal_type"] != "cycle":
            continue
        normalized = _normalize_cycle(chain["cycle"])
        key = tuple(normalized)
        if key not in seen_cycles:
            seen_cycles.add(key)
            cycles.append(normalized)

    return {
        "system": "Classical sign rulership",
        "chains": chains,
        "final_dispositors": final_dispositors,
        "cycles": cycles,
        "note": (
            "A dispositor chain shows sign-rulership dependency. A final "
            "dispositor or cycle is structural context, not a standalone verdict."
        ),
    }


def _trace_chain(start_planet: str, chart: dict) -> dict:
    direct_dispositor = SIGN_RULERS[chart["planets"][start_planet]["sign"]]
    path = [start_planet]
    positions = {start_planet: 0}
    current = start_planet

    while True:
        next_planet = SIGN_RULERS[chart["planets"][current]["sign"]]

        if next_planet == current:
            return {
                "direct_dispositor": direct_dispositor,
                "path": path,
                "terminal_type": "final_dispositor",
                "terminal_dispositor": current,
                "cycle": [],
            }

        if next_planet in positions:
            return {
                "direct_dispositor": direct_dispositor,
                "path": path,
                "terminal_type": "cycle",
                "terminal_dispositor": None,
                "cycle": path[positions[next_planet]:],
            }

        path.append(next_planet)
        positions[next_planet] = len(path) - 1
        current = next_planet


def _normalize_cycle(cycle: list[str]) -> list[str]:
    """Rotate a cycle to a stable representation for de-duplication."""
    if not cycle:
        return []
    rotations = [
        cycle[index:] + cycle[:index]
        for index in range(len(cycle))
    ]
    return min(rotations)
