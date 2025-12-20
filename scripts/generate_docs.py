#!/usr/bin/env python3
"""Auto-generate entity documentation for the Kiosker integration."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - fallback to lightweight parser
    yaml = None

INTEGRATION_PATH = Path(__file__).resolve().parents[1]
COMPONENT_PATH = INTEGRATION_PATH / "custom_components" / "kiosker"
DOCS_PATH = INTEGRATION_PATH / "docs" / "entities.md"

UNIT_VALUE_MAP = {
    "PERCENTAGE": "%",
    "LIGHT_LUX": "lux",
    "LUX": "lux",
    "ILLUMINANCE_UNIT": "lux",
}

CATEGORY_MAP = {
    "DIAGNOSTIC": "Diagnostic",
    "CONFIG": "Configuration",
}


def parse_python_file(file_path: Path) -> ast.AST | None:
    """Parse a Python file and return its AST."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as err:  # pragma: no cover - best effort logging
        print(f"Error reading {file_path}: {err}")
        return None

    try:
        return ast.parse(content)
    except SyntaxError as err:  # pragma: no cover - best effort logging
        print(f"Syntax error in {file_path}: {err}")
        return None


def safe_eval(node: ast.AST, values: dict[str, Any]) -> Any:
    """Safely evaluate simple AST nodes for constants."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return values.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = safe_eval(node.value, values)
        if isinstance(base, str):
            return f"{base}.{node.attr}"
        return node.attr
    if isinstance(node, ast.Dict):
        return {
            safe_eval(key, values): safe_eval(value, values)
            for key, value in zip(node.keys, node.values)
        }
    if isinstance(node, ast.List):
        return [safe_eval(elt, values) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return [safe_eval(elt, values) for elt in node.elts]
    if isinstance(node, ast.JoinedStr):
        return render_fstring(node, values)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        operand = safe_eval(node.operand, values)
        if isinstance(operand, (int, float)):
            return -operand
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = safe_eval(node.left, values)
        right = safe_eval(node.right, values)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
    return None


def render_fstring(node: ast.JoinedStr, values: dict[str, Any]) -> str:
    """Render a best-effort f-string representation."""
    rendered_parts: list[str] = []
    for part in node.values:
        if isinstance(part, ast.Constant):
            rendered_parts.append(str(part.value))
        elif isinstance(part, ast.FormattedValue):
            rendered = safe_eval(part.value, values)
            rendered_parts.append(str(rendered))
    return "".join(rendered_parts)


def load_const_values(tree: ast.AST | None) -> dict[str, Any]:
    """Load constant values from a parsed AST tree."""
    if not tree:
        return {}

    values: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            value = safe_eval(node.value, values)
            if value is None:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    values[target.id] = value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.value is not None:
                value = safe_eval(node.value, values)
                if value is not None:
                    values[node.target.id] = value
    return values


def render_value(node: ast.AST, values: dict[str, Any], kind: str | None = None) -> Any:
    """Render a best-effort string value from an AST node."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return values.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        if kind in {"device_class", "state_class", "entity_category"}:
            return node.attr
        base = render_value(node.value, values, kind)
        if isinstance(base, str):
            return f"{base}.{node.attr}"
        return node.attr
    if isinstance(node, ast.JoinedStr):
        return render_fstring(node, values)
    if isinstance(node, ast.List):
        return [render_value(elt, values, kind) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return [render_value(elt, values, kind) for elt in node.elts]
    return safe_eval(node, values)


def extract_description_calls(
    tree: ast.AST | None, variable_name: str
) -> list[ast.Call]:
    """Find tuple/list assignments to a variable and return call nodes."""
    if not tree:
        return []

    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == variable_name
            for target in node.targets
        ):
            if isinstance(node.value, (ast.Tuple, ast.List)):
                return [
                    item
                    for item in node.value.elts
                    if isinstance(item, ast.Call)
                ]
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == variable_name
            and isinstance(node.value, (ast.Tuple, ast.List))
        ):
            return [
                item
                for item in node.value.elts
                if isinstance(item, ast.Call)
            ]
    return []


def lambda_to_source(node: ast.AST) -> str | None:
    """Convert lambda expression body to a readable source path."""
    if isinstance(node, ast.Lambda):
        return expression_to_source(node.body)
    return None


def expression_to_source(node: ast.AST) -> str | None:
    """Render an expression node to a readable string."""
    if hasattr(ast, "unparse"):
        try:
            rendered = ast.unparse(node)
        except Exception:  # pragma: no cover - best effort
            rendered = None
    else:  # pragma: no cover
        rendered = None

    if rendered:
        return rendered.replace("data.", "")

    if isinstance(node, ast.Attribute):
        parts: list[str] = []
        current: ast.AST | None = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name) and current.id == "data":
            parts.append("data")
        parts.reverse()
        return ".".join(part for part in parts if part != "data")

    return None


def parse_description(call: ast.Call, values: dict[str, Any]) -> dict[str, Any]:
    """Parse a description call into a dictionary of attributes."""
    data: dict[str, Any] = {"_class": None}
    if isinstance(call.func, ast.Name):
        data["_class"] = call.func.id
    elif isinstance(call.func, ast.Attribute):
        data["_class"] = call.func.attr

    for kw in call.keywords:
        if kw.arg is None:
            continue
        if kw.arg == "value_fn":
            data["value_fn"] = lambda_to_source(kw.value) or expression_to_source(
                kw.value
            )
            continue
        data[kw.arg] = render_value(kw.value, values, kind=kw.arg)

    return data


def format_unit(value: Any) -> str:
    """Format unit values for display."""
    if value is None:
        return "-"
    if isinstance(value, str):
        mapped = UNIT_VALUE_MAP.get(value)
        if mapped:
            return mapped
        if "." in value:
            return UNIT_VALUE_MAP.get(value.split(".")[-1], value.split(".")[-1])
        return value
    return str(value)


def format_enum(value: Any) -> str:
    """Format enum-like values for display."""
    if value is None:
        return "-"
    if isinstance(value, str):
        token = value.split(".")[-1]
        return token.replace("_", " ").title()
    return str(value)


def format_category(value: Any) -> str:
    """Format entity category value for display."""
    if value is None:
        return "Primary"
    if isinstance(value, str):
        token = value.split(".")[-1]
        for key, label in CATEGORY_MAP.items():
            if key in token:
                return label
        return token.replace("_", " ").title()
    return str(value)


def format_icon(value: Any, key: str | None = None) -> str:
    """Format icon value, accounting for dynamic icons."""
    if key == "battery_state":
        return "dynamic (battery level)"
    if value is None:
        return "-"
    if isinstance(value, str):
        return value
    return str(value)


def format_source(value: Any) -> str:
    """Format a value source string."""
    if not value:
        return "-"
    return str(value)


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a markdown table."""
    table = "| " + " | ".join(sanitize_cell(header) for header in headers) + " |\n"
    table += "|" + "|".join(["---" for _ in headers]) + "|\n"
    for row in rows:
        table += "| " + " | ".join(sanitize_cell(cell) for cell in row) + " |\n"
    return table


def sanitize_cell(value: Any) -> str:
    """Escape table cell content to avoid breaking Markdown tables."""
    text = str(value)
    return text.replace("|", "\\|")


def extract_dataclass_fields(tree: ast.AST | None, class_name: str) -> list[tuple[str, str]]:
    """Extract annotated dataclass fields from a class definition."""
    if not tree:
        return []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            fields: list[tuple[str, str]] = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    field_name = item.target.id
                    field_type = "-"
                    if item.annotation is not None and hasattr(ast, "unparse"):
                        try:
                            field_type = ast.unparse(item.annotation)
                        except Exception:
                            field_type = "-"
                    fields.append((field_name, field_type))
            return fields
    return []


def extract_action_calls(tree: ast.AST | None) -> dict[str, list[str]]:
    """Extract button action to client call mapping."""
    if not tree:
        return {}

    mapping: dict[str, list[str]] = {}

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "KioskerActionButton":
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef) and item.name == "async_press":
                    mapping.update(parse_if_chain(item.body))
                    return mapping

    return mapping


def parse_if_chain(nodes: list[ast.stmt]) -> dict[str, list[str]]:
    """Parse if/elif chains for action mappings."""
    mapping: dict[str, list[str]] = {}
    for node in nodes:
        if isinstance(node, ast.If):
            action = parse_action_test(node.test)
            if action:
                mapping[action] = collect_client_calls(node.body)
            mapping.update(parse_if_chain(node.orelse))
    return mapping


def parse_action_test(node: ast.AST) -> str | None:
    """Parse `action == "..."` comparisons."""
    if not isinstance(node, ast.Compare):
        return None
    if not (isinstance(node.left, ast.Name) and node.left.id == "action"):
        return None
    if len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
        return None
    if len(node.comparators) != 1:
        return None
    comparator = node.comparators[0]
    if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
        return comparator.value
    return None


def collect_client_calls(nodes: list[ast.stmt]) -> list[str]:
    """Collect awaited client method calls in a list of statements."""
    calls: list[str] = []
    for node in ast.walk(ast.Module(body=nodes, type_ignores=[])):
        if isinstance(node, ast.Await) and isinstance(node.value, ast.Call):
            func = node.value.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "client"
            ):
                calls.append(func.attr)
    return calls


def load_services(service_path: Path) -> dict[str, Any]:
    """Load services.yaml into a dictionary."""
    try:
        content = service_path.read_text(encoding="utf-8")
    except Exception as err:  # pragma: no cover - best effort logging
        print(f"Error reading {service_path}: {err}")
        return {}

    if yaml is not None:
        data = yaml.safe_load(content)
    else:
        data = parse_simple_yaml(content)
    if not isinstance(data, dict):
        return {}
    return data


def parse_simple_yaml(content: str) -> dict[str, Any]:
    """Parse a minimal subset of YAML used by services.yaml."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(0, root)]

    for raw_line in content.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        while stack and indent < stack[-1][0]:
            stack.pop()

        if not stack:
            stack = [(0, root)]

        current = stack[-1][1]

        if value == "":
            new_dict: dict[str, Any] = {}
            current[key] = new_dict
            stack.append((indent + 2, new_dict))
            continue

        current[key] = parse_scalar(value)

    return root


def parse_scalar(value: str) -> Any:
    """Parse a scalar value from simple YAML content."""
    if value == "{}":
        return {}
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.isdigit():
        return int(value)
    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def format_selector(selector: Any) -> str:
    """Format selector metadata for docs."""
    if not selector:
        return "-"
    if isinstance(selector, dict) and len(selector) == 1:
        selector_type = next(iter(selector))
        details = selector[selector_type]
        if isinstance(details, dict) and details:
            detail_parts = []
            for key in (
                "type",
                "mode",
                "min",
                "max",
                "unit_of_measurement",
                "multiline",
            ):
                if key in details:
                    detail_parts.append(f"{key}={details[key]}")
            if detail_parts:
                return f"{selector_type} ({', '.join(detail_parts)})"
        return selector_type
    return str(selector)


def build_docs() -> str:
    """Build the full documentation content."""
    sensor_tree = parse_python_file(COMPONENT_PATH / "sensor.py")
    binary_tree = parse_python_file(COMPONENT_PATH / "binary_sensor.py")
    button_tree = parse_python_file(COMPONENT_PATH / "button.py")
    api_tree = parse_python_file(COMPONENT_PATH / "api.py")

    sensor_values = load_const_values(sensor_tree)
    binary_values = load_const_values(binary_tree)
    button_values = load_const_values(button_tree)

    sensors = [
        parse_description(call, sensor_values)
        for call in extract_description_calls(sensor_tree, "SENSORS")
    ]
    binary_sensors = [
        parse_description(call, binary_values)
        for call in extract_description_calls(binary_tree, "BINARY_SENSORS")
    ]
    buttons = [
        parse_description(call, button_values)
        for call in extract_description_calls(button_tree, "BUTTONS")
    ]

    action_map = extract_action_calls(button_tree)
    services = load_services(COMPONENT_PATH / "services.yaml")

    status_fields = extract_dataclass_fields(api_tree, "DeviceStatus")
    screensaver_fields = extract_dataclass_fields(api_tree, "ScreensaverState")
    blackout_fields = extract_dataclass_fields(api_tree, "BlackoutState")

    lines: list[str] = []
    lines.append("---")
    lines.append("title: Entity Reference")
    lines.append(
        "description: Auto-generated reference for sensors, binary sensors, buttons, and services exposed by the Kiosker integration."
    )
    lines.append("---\n")

    lines.append("# Entity Reference\n")
    lines.append("> This page is auto-generated by `scripts/generate_docs.py`. Do not edit manually.\n")
    lines.append(
        "This page provides a comprehensive reference of all entities and services exposed by the Kiosker integration."
    )
    lines.append("\n## Overview\n")
    lines.append("Entities are created per kiosk device from the data returned by the Kiosker API.")
    lines.append(
        "Each entity uses a unique ID of the form `<device_id>_<entity_key>` and derives its name from the entity description."
    )

    if status_fields:
        lines.append("\n## Data payloads\n")
        lines.append("### Status payload\n")
        lines.append(
            "The status payload is fetched from the `status` endpoint and provides the fields below."
        )
        lines.append("")
        rows = [[name, type_name] for name, type_name in status_fields]
        lines.append(render_table(["Field", "Type"], rows))
    if screensaver_fields:
        lines.append("\n### Screensaver payload\n")
        lines.append("")
        rows = [[name, type_name] for name, type_name in screensaver_fields]
        lines.append(render_table(["Field", "Type"], rows))
    if blackout_fields:
        lines.append("\n### Blackout payload\n")
        lines.append("")
        rows = [[name, type_name] for name, type_name in blackout_fields]
        lines.append(render_table(["Field", "Type"], rows))

    if sensors:
        lines.append("\n## Sensors\n")
        lines.append("")
        rows: list[list[str]] = []
        for sensor in sorted(sensors, key=lambda item: item.get("name", "")):
            key = str(sensor.get("key", "-"))
            source = format_source(sensor.get("value_fn"))
            description = (
                f"Value from `{source}`." if source != "-" else "-"
            )
            rows.append(
                [
                    str(sensor.get("name", "-")),
                    key,
                    description,
                    format_enum(sensor.get("device_class")),
                    format_unit(sensor.get("native_unit_of_measurement")),
                    format_enum(sensor.get("state_class")),
                    format_category(sensor.get("entity_category")),
                    format_icon(sensor.get("icon"), key=key),
                    source,
                ]
            )
        lines.append(
            render_table(
                [
                    "Name",
                    "Key",
                    "Description",
                    "Device Class",
                    "Unit",
                    "State Class",
                    "Category",
                    "Icon",
                    "Source",
                ],
                rows,
            )
        )

    if binary_sensors:
        lines.append("\n## Binary sensors\n")
        lines.append("")
        rows = []
        for sensor in sorted(binary_sensors, key=lambda item: item.get("name", "")):
            key = str(sensor.get("key", "-"))
            source = format_source(sensor.get("value_fn"))
            description = (
                f"True when `{source}` is truthy." if source != "-" else "-"
            )
            rows.append(
                [
                    str(sensor.get("name", "-")),
                    key,
                    description,
                    format_category(sensor.get("entity_category")),
                    format_icon(sensor.get("icon"), key=key),
                    source,
                ]
            )
        lines.append(
            render_table(
                ["Name", "Key", "Description", "Category", "Icon", "Source"], rows
            )
        )

    if buttons:
        lines.append("\n## Buttons\n")
        lines.append("")
        rows = []
        for button in sorted(buttons, key=lambda item: item.get("name", "")):
            action = str(button.get("action", "-"))
            client_calls = action_map.get(action, [])
            calls_text = ", ".join(client_calls) if client_calls else "-"
            rows.append(
                [
                    str(button.get("name", "-")),
                    str(button.get("key", "-")),
                    action,
                    format_category(button.get("entity_category")),
                    format_icon(button.get("icon")),
                    calls_text,
                ]
            )
        lines.append(
            render_table(
                ["Name", "Key", "Action", "Category", "Icon", "API Call(s)"], rows
            )
        )

    lines.append("\n## Services\n")
    if services:
        lines.append(
            "All services are registered under the `kiosker` domain. Use `device_id` when multiple kiosks are configured."
        )
        for service_key in sorted(services):
            service = services[service_key]
            title = f"kiosker.{service_key}"
            description = service.get("description", "-")
            lines.append(f"\n### `{title}`\n")
            lines.append(description)

            fields = service.get("fields", {})
            if fields:
                lines.append("")
                rows = []
                for field_key in fields:
                    field = fields[field_key]
                    rows.append(
                        [
                            field_key,
                            "yes" if field.get("required") else "no",
                            field.get("description", "-"),
                            str(field.get("example", "-")),
                            format_selector(field.get("selector")),
                        ]
                    )
                lines.append(
                    render_table(
                        ["Field", "Required", "Description", "Example", "Selector"],
                        rows,
                    )
                )
    else:
        lines.append("No services are currently defined.")

    lines.append("\n## Entity naming and IDs\n")
    lines.append(
        "Kiosker entities use Home Assistant's entity naming with `has_entity_name`, "
        "so entity names are derived from the device name and the entity description."
    )
    lines.append(
        "Unique IDs are created from the kiosk device ID and the entity key: `device_id_<key>`."
    )

    lines.append("\n## Diagnostics\n")
    lines.append(
        "Use Settings -> Devices & Services -> Kiosker -> Download diagnostics to capture a sanitized snapshot of the latest payloads."
    )

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    """Generate entity documentation."""
    docs_content = build_docs()
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.write_text(docs_content, encoding="utf-8")
    print(f"Generated entity documentation: {DOCS_PATH}")


if __name__ == "__main__":
    main()
