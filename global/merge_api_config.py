#!/usr/bin/env python3
"""
merge_api_config.py
-------------------
Merges three layers into a single api.yaml before apictl import:

  Layer 1 (base)     : global/api-template.yaml   - platform-wide defaults
  Layer 2 (domain)   : global/domain-visibility.yaml - visibility per domain
  Layer 3 (override) : <api_path>/api.yaml         - API-specific values

Rules:
  - Layer 3 wins over Layer 2 wins over Layer 1 for all scalar fields.
  - visibleRoles is unioned across all layers (never replaced).
  - visibility from the domain layer always wins over the global default,
    but an explicit visibility in api.yaml wins over the domain layer.

Usage:
  python3 global/merge_api_config.py <api_path> <domain>

  <api_path>  : path to the API folder, e.g. domains/finance/orders-api
  <domain>    : domain name, e.g. finance | integration | public

Output:
  Overwrites <api_path>/api.yaml with the merged result.
"""

import sys
import yaml
from pathlib import Path


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Override wins on scalar conflicts."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def union_list(a: list, b: list) -> list:
    """Return sorted union of two lists, preserving unique values."""
    return sorted(set(a) | set(b))


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <api_path> <domain>", file=sys.stderr)
        sys.exit(1)

    api_path = Path(sys.argv[1])
    domain = sys.argv[2].lower()

    repo_root = Path(__file__).parent.parent
    global_template_path = repo_root / "global" / "api-template.yaml"
    domain_visibility_path = repo_root / "global" / "domain-visibility.yaml"
    api_yaml_path = api_path / "api.yaml"

    # --- Load all three layers ---
    global_cfg = load_yaml(global_template_path)
    domain_vis_cfg = load_yaml(domain_visibility_path)
    api_cfg = load_yaml(api_yaml_path)

    # --- Layer 1: global template (data section only) ---
    merged_data = global_cfg.get("data", {}).copy()

    # --- Layer 2: domain visibility ---
    domain_rules = domain_vis_cfg.get("domains", {}).get(domain)
    if domain_rules is None:
        print(
            f"WARNING: domain '{domain}' not found in domain-visibility.yaml. "
            "Keeping global default visibility.",
            file=sys.stderr,
        )
        domain_visibility = None
        domain_roles = []
    else:
        domain_visibility = domain_rules.get("visibility")
        domain_roles = domain_rules.get("visibleRoles", [])

    if domain_visibility:
        merged_data["visibility"] = domain_visibility

    # --- Layer 3: API-level overrides ---
    api_data = api_cfg.get("data", {})

    # Pull out visibleRoles from api.yaml before the deep merge so we can union
    api_roles = api_data.pop("visibleRoles", [])

    # Deep-merge api-level data (api_data wins over merged_data)
    merged_data = deep_merge(merged_data, api_data)

    # Union visibleRoles: domain roles + api-level roles
    all_roles = union_list(domain_roles, api_roles)

    # Only set visibleRoles if there are any (avoid empty list on PUBLIC/PRIVATE)
    if all_roles:
        merged_data["visibleRoles"] = all_roles
    else:
        merged_data.pop("visibleRoles", None)

    # --- Build final structure ---
    output = {
        "type": api_cfg.get("type", global_cfg.get("type", "api")),
        "version": api_cfg.get("version", global_cfg.get("version", "v4.3.0")),
        "data": merged_data,
    }

    # --- Write result back to api.yaml ---
    with open(api_yaml_path, "w") as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(
        f"Merged api.yaml written for {api_path} "
        f"(domain={domain}, visibility={merged_data.get('visibility')}, "
        f"visibleRoles={merged_data.get('visibleRoles', [])})"
    )


if __name__ == "__main__":
    main()
