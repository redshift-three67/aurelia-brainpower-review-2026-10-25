from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
APP_CSS = ROOT / "apps" / "web" / "static" / "app.css"


@dataclass(frozen=True)
class _CssBlock:
    start: int
    end: int
    body_start: int
    body_end: int


@dataclass(frozen=True)
class _CssNode:
    tag: str
    element_id: str = ""
    classes: tuple[str, ...] = ()
    attributes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class _CssTarget:
    node: _CssNode
    ancestors: tuple[_CssNode, ...]


_FINALIZE_PHASE = _CssNode(
    "section",
    "finalize-phase",
    ("panel", "wizard-panel", "phase-analyse"),
    (("data-step", "10"),),
)
_REPORTS_LAYOUT = _CssNode("div", classes=("reports-layout",))
_REPORT_CATALOG = _CssNode(
    "aside",
    "report-catalog-panel",
    ("reports-column", "report-catalog-panel"),
    (
        ("aria-labelledby", "reports-heading"),
        ("aria-label", "Berichtskatalog"),
    ),
)
_REPORT_LIST = _CssNode(
    "div",
    "report-list",
    ("report-list", "scroll-region"),
    (
        ("role", "toolbar"),
        ("aria-label", "Berichte auswaehlen"),
        ("aria-orientation", "horizontal"),
        ("aria-live", "polite"),
    ),
)
_REPORT_SESSION = _CssNode(
    "details",
    classes=("report-session-group",),
    attributes=(("open", ""),),
)
_REPORT_CLIENT = _CssNode(
    "details",
    classes=("report-client-group",),
    attributes=(("open", ""),),
)
_REPORT_ITEM = _CssNode(
    "button",
    classes=("report-item",),
    attributes=(
        ("type", "button"),
        ("data-report-id", "known-report"),
        ("aria-pressed", "false"),
    ),
)
_REPORT_PREVIEW = _CssNode(
    "div",
    "report-preview-panel",
    ("reports-column", "report-preview-column", "report-preview-panel"),
    (("aria-label", "Berichtsvorschau"),),
)
_GATE4_CSS_TARGETS = {
    ".reports-layout": _CssTarget(_REPORTS_LAYOUT, (_FINALIZE_PHASE,)),
    ".report-list": _CssTarget(
        _REPORT_LIST,
        (_REPORT_CATALOG, _REPORTS_LAYOUT, _FINALIZE_PHASE),
    ),
    ".report-item": _CssTarget(
        _REPORT_ITEM,
        (
            _REPORT_SESSION,
            _REPORT_CLIENT,
            _REPORT_LIST,
            _REPORT_CATALOG,
            _REPORTS_LAYOUT,
            _FINALIZE_PHASE,
        ),
    ),
    ".report-preview-column": _CssTarget(
        _REPORT_PREVIEW,
        (_REPORTS_LAYOUT, _FINALIZE_PHASE),
    ),
}


def _matching_css_brace(source: str, opening_brace: int) -> int:
    depth = 0
    index = opening_brace
    quote = ""
    while index < len(source):
        if quote:
            if source[index] == "\\":
                index += 2
                continue
            if source[index] == quote:
                quote = ""
        elif source.startswith("/*", index):
            comment_end = source.find("*/", index + 2)
            assert comment_end >= 0, "unterminated CSS comment"
            index = comment_end + 2
            continue
        elif source[index] in {'"', "'"}:
            quote = source[index]
        elif source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise AssertionError("unterminated CSS block")


def _css_without_comments(source: str) -> str:
    return re.sub(
        r"/\*.*?\*/",
        lambda match: "".join(
            "\n" if character == "\n" else " " for character in match.group()
        ),
        source,
        flags=re.DOTALL,
    )


def _css_blocks(source: str, header: str) -> list[_CssBlock]:
    searchable = _css_without_comments(source)
    blocks: list[_CssBlock] = []
    for match in re.finditer(
        rf"(?m)^[ \t]*{re.escape(header)}[ \t]*\{{",
        searchable,
    ):
        opening_brace = searchable.rfind("{", match.start(), match.end())
        closing_brace = _matching_css_brace(source, opening_brace)
        blocks.append(
            _CssBlock(
                start=match.start(),
                end=closing_brace + 1,
                body_start=opening_brace + 1,
                body_end=closing_brace,
            )
        )
    return blocks


def _direct_css_blocks(
    source: str,
    start: int = 0,
    end: int | None = None,
) -> list[tuple[_CssBlock, str]]:
    container_end = len(source) if end is None else end
    blocks: list[tuple[_CssBlock, str]] = []
    item_start = start
    index = start
    quote = ""
    parenthesis_depth = 0
    bracket_depth = 0
    while index < container_end:
        character = source[index]
        if quote:
            if character == "\\":
                index += 2
                continue
            if character == quote:
                quote = ""
        elif source.startswith("/*", index):
            comment_end = source.find("*/", index + 2)
            assert comment_end >= 0, "unterminated CSS comment"
            index = comment_end + 2
            continue
        elif character in {'"', "'"}:
            quote = character
        elif character == "(":
            parenthesis_depth += 1
        elif character == ")":
            parenthesis_depth -= 1
        elif character == "[":
            bracket_depth += 1
        elif character == "]":
            bracket_depth -= 1
        elif (
            character == ";"
            and parenthesis_depth == 0
            and bracket_depth == 0
        ):
            item_start = index + 1
        elif (
            character == "{"
            and parenthesis_depth == 0
            and bracket_depth == 0
        ):
            closing_brace = _matching_css_brace(source, index)
            assert closing_brace < container_end, "CSS block exceeds container"
            header = _css_without_comments(source[item_start:index]).strip()
            if header:
                blocks.append(
                    (
                        _CssBlock(
                            start=item_start,
                            end=closing_brace + 1,
                            body_start=index + 1,
                            body_end=closing_brace,
                        ),
                        header,
                    )
                )
            index = closing_brace + 1
            item_start = index
            continue
        index += 1
    return blocks


def _css_media_blocks(source: str) -> list[tuple[_CssBlock, str]]:
    media_blocks: list[tuple[_CssBlock, str]] = []

    def collect(start: int, end: int) -> None:
        for block, header in _direct_css_blocks(source, start, end):
            media_match = re.match(r"@media\s+(.+)$", header, re.IGNORECASE | re.DOTALL)
            if not media_match:
                continue
            media_blocks.append(
                (block, " ".join(media_match.group(1).split()))
            )
            collect(block.body_start, block.body_end)

    collect(0, len(source))
    return media_blocks


def _css_style_blocks(source: str) -> list[tuple[_CssBlock, str]]:
    rules: list[tuple[_CssBlock, str]] = []

    def collect(start: int, end: int) -> None:
        for block, header in _direct_css_blocks(source, start, end):
            if re.match(r"@media\b", header, re.IGNORECASE):
                collect(block.body_start, block.body_end)
            elif not header.startswith("@"):
                rules.append((block, header))

    collect(0, len(source))
    return rules


def _split_css_selector_list(header: str) -> list[str]:
    selectors: list[str] = []
    start = 0
    bracket_depth = 0
    parenthesis_depth = 0
    quote = ""
    for index, character in enumerate(header):
        if quote:
            if character == quote and header[index - 1 : index] != "\\":
                quote = ""
        elif character in {'"', "'"}:
            quote = character
        elif character == "[":
            bracket_depth += 1
        elif character == "]":
            bracket_depth -= 1
        elif character == "(":
            parenthesis_depth += 1
        elif character == ")":
            parenthesis_depth -= 1
        elif character == "," and bracket_depth == parenthesis_depth == 0:
            selectors.append(header[start:index].strip())
            start = index + 1
    selectors.append(header[start:].strip())
    return [selector for selector in selectors if selector]


def _selector_compounds(selector: str) -> list[str]:
    compounds: list[str] = []
    start = 0
    bracket_depth = 0
    quote = ""
    index = 0
    while index < len(selector):
        character = selector[index]
        if quote:
            if character == "\\":
                index += 2
                continue
            if character == quote:
                quote = ""
        elif character in {'"', "'"}:
            quote = character
        elif character == "[":
            bracket_depth += 1
        elif character == "]":
            bracket_depth -= 1
        elif bracket_depth == 0 and character in ">+~":
            return []
        elif bracket_depth == 0 and character.isspace():
            if selector[start:index].strip():
                compounds.append(selector[start:index].strip())
            while index + 1 < len(selector) and selector[index + 1].isspace():
                index += 1
            start = index + 1
        index += 1
    if selector[start:].strip():
        compounds.append(selector[start:].strip())
    return compounds


def _node_attribute(node: _CssNode, name: str) -> str | None:
    if name == "id":
        return node.element_id or None
    if name == "class":
        return " ".join(node.classes) or None
    return dict(node.attributes).get(name)


def _compound_specificity(
    compound: str,
    node: _CssNode,
) -> tuple[int, int, int] | None:
    ids = 0
    classes_and_attributes = 0
    types = 0
    index = 0
    type_match = re.match(r"(?:\*|[a-zA-Z][\w-]*)", compound)
    if type_match:
        type_name = type_match.group()
        if type_name != "*" and type_name.lower() != node.tag.lower():
            return None
        if type_name != "*":
            types += 1
        index = type_match.end()

    while index < len(compound):
        token = compound[index]
        if token == "#":
            match = re.match(r"#([\w-]+)", compound[index:])
            if not match or match.group(1) != node.element_id:
                return None
            ids += 1
        elif token == ".":
            match = re.match(r"\.([\w-]+)", compound[index:])
            if not match or match.group(1) not in node.classes:
                return None
            classes_and_attributes += 1
        elif token == "[":
            match = re.match(
                r"\[\s*([\w:-]+)\s*(?:(=|~=)\s*(?:\"([^\"]*)\"|'([^']*)'|([^\]\s]+)))?\s*\]",
                compound[index:],
            )
            if not match:
                return None
            actual = _node_attribute(node, match.group(1).lower())
            if actual is None:
                return None
            operator = match.group(2)
            expected = next(
                (value for value in match.groups()[2:] if value is not None),
                None,
            )
            if operator == "=" and actual != expected:
                return None
            if operator == "~=" and expected not in actual.split():
                return None
            classes_and_attributes += 1
        else:
            # Dynamic pseudo states and unsupported combinators are not active
            # for these static Gate 4 contract elements.
            return None
        index += len(match.group())
    return ids, classes_and_attributes, types


def _selector_specificity(
    selector: str,
    target: _CssTarget,
) -> tuple[int, int, int] | None:
    compounds = _selector_compounds(selector)
    if not compounds:
        return None
    specificity = _compound_specificity(compounds[-1], target.node)
    if specificity is None:
        return None

    ancestor_index = 0
    for compound in reversed(compounds[:-1]):
        while ancestor_index < len(target.ancestors):
            ancestor_specificity = _compound_specificity(
                compound,
                target.ancestors[ancestor_index],
            )
            ancestor_index += 1
            if ancestor_specificity is not None:
                specificity = tuple(
                    left + right
                    for left, right in zip(specificity, ancestor_specificity)
                )
                break
        else:
            return None
    return specificity


def _css_declarations(
    source: str,
    block: _CssBlock,
) -> list[tuple[str, str, bool, int]]:
    declarations: list[tuple[str, str, bool, int]] = []
    body = source[block.body_start : block.body_end]
    segment_start = 0
    index = 0
    quote = ""
    parenthesis_depth = 0
    bracket_depth = 0
    segments: list[tuple[int, str]] = []
    while index < len(body):
        character = body[index]
        if quote:
            if character == "\\":
                index += 2
                continue
            if character == quote:
                quote = ""
        elif body.startswith("/*", index):
            comment_end = body.find("*/", index + 2)
            assert comment_end >= 0, "unterminated CSS declaration comment"
            index = comment_end + 2
            continue
        elif character in {'"', "'"}:
            quote = character
        elif character == "(":
            parenthesis_depth += 1
        elif character == ")":
            parenthesis_depth -= 1
        elif character == "[":
            bracket_depth += 1
        elif character == "]":
            bracket_depth -= 1
        elif (
            character == ";"
            and parenthesis_depth == 0
            and bracket_depth == 0
        ):
            segments.append((segment_start, body[segment_start:index]))
            segment_start = index + 1
        index += 1
    segments.append((segment_start, body[segment_start:]))

    for source_offset, segment in segments:
        cleaned = _css_without_comments(segment)
        match = re.match(
            r"\s*([a-z-]+)\s*:\s*(.*?)\s*$",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not match:
            continue
        value = match.group(2)
        important_match = re.search(
            r"\s*!\s*important\s*$",
            value,
            re.IGNORECASE,
        )
        important = important_match is not None
        if important_match:
            value = value[: important_match.start()].rstrip()
        declarations.append(
            (
                match.group(1).lower(),
                value,
                important,
                block.body_start + source_offset,
            )
        )
    return declarations


def _width_media_applies(condition: str, viewport_width: int) -> bool:
    for alternative in _split_css_selector_list(condition.lower()):
        query = alternative.strip()
        media_match = re.match(
            r"(?:(only|not)\s+)?(all|screen|print|speech)\b",
            query,
        )
        if media_match:
            modifier, media_type = media_match.groups()
            media_type_applies = media_type in {"all", "screen"}
            query = query[media_match.end() :].strip()
            if query.startswith("and"):
                query = query[3:].strip()
        elif query and not query.startswith("("):
            continue
        else:
            modifier = None
            media_type_applies = True

        features = re.findall(r"\(([^()]*)\)", query)
        if not features and query:
            continue
        limits: list[tuple[str, str]] = []
        supported = True
        for feature in features:
            width_match = re.fullmatch(
                r"\s*(min|max)-width\s*:\s*(\d+)px\s*",
                feature,
            )
            if not width_match:
                supported = False
                break
            limits.append(width_match.groups())
        if not supported:
            continue
        query_applies = media_type_applies and all(
            viewport_width >= int(value)
            if boundary == "min"
            else viewport_width <= int(value)
            for boundary, value in limits
        )
        if modifier == "not":
            query_applies = not query_applies
        if query_applies:
            return True
    return False


def _effective_css_declarations(
    source: str,
    selector: str,
    viewport_width: int,
) -> dict[str, str]:
    target = _GATE4_CSS_TARGETS.get(selector)
    assert target is not None, f"unknown Gate 4 CSS target: {selector}"
    media_blocks = _css_media_blocks(source)
    winners: dict[str, tuple[tuple[bool, int, int, int, int], str]] = {}
    matched = False
    for rule, header in _css_style_blocks(source):
        enclosing_media = [
            condition
            for media, condition in media_blocks
            if media.start < rule.start and rule.end <= media.end
        ]
        if enclosing_media and not all(
            _width_media_applies(condition, viewport_width)
            for condition in enclosing_media
        ):
            continue
        matching_specificities = [
            specificity
            for branch in _split_css_selector_list(header)
            if (
                specificity := _selector_specificity(branch, target)
            )
            is not None
        ]
        if not matching_specificities:
            continue
        specificity = max(matching_specificities)
        for name, value, important, source_order in _css_declarations(source, rule):
            cascade_key = (important, *specificity, source_order)
            expanded = ((name, value),)
            if name == "overflow":
                overflow_values = value.split()
                if len(overflow_values) == 1:
                    expanded = (
                        ("overflow-x", overflow_values[0]),
                        ("overflow-y", overflow_values[0]),
                    )
                elif len(overflow_values) == 2:
                    expanded = (
                        ("overflow-x", overflow_values[0]),
                        ("overflow-y", overflow_values[1]),
                    )
            for expanded_name, expanded_value in expanded:
                if (
                    expanded_name not in winners
                    or cascade_key >= winners[expanded_name][0]
                ):
                    winners[expanded_name] = (cascade_key, expanded_value)
        matched = True
    assert matched, f"no applicable CSS rule for {selector} at {viewport_width}px"
    return {name: winner[1] for name, winner in winners.items()}


def _assert_effective_css_declarations(
    source: str,
    selector: str,
    viewport_width: int,
    expected: dict[str, str],
) -> None:
    actual = _effective_css_declarations(source, selector, viewport_width)
    assert {name: actual.get(name) for name in expected} == expected


def _replace_css_declaration(
    source: str,
    block: _CssBlock,
    old: str,
    new: str,
) -> str:
    body = source[block.body_start : block.body_end]
    mutated_body = body.replace(old, new, 1)
    assert mutated_body != body, f"missing mutation target: {old}"
    return source[: block.body_start] + mutated_body + source[block.body_end :]


def _assert_static_css_node(html: str, node: _CssNode) -> None:
    for match in re.finditer(r"<([a-zA-Z][\w:-]*)\b([^<>]*)>", html):
        attributes = dict(re.findall(r'([\w:-]+)="([^"]*)"', match.group(2)))
        if node.element_id:
            identity_matches = attributes.get("id") == node.element_id
        else:
            identity_matches = bool(node.classes) and node.classes[0] in (
                attributes.get("class", "").split()
            )
        if not identity_matches:
            continue
        assert match.group(1).lower() == node.tag
        assert tuple(attributes.get("class", "").split()) == node.classes
        for name, value in node.attributes:
            assert attributes.get(name) == value
        return
    raise AssertionError(f"missing static Gate 4 node: {node}")


def _assert_gate4_report_layout_contract(html: str, css: str) -> None:
    phase = html.split('id="finalize-phase"', 1)[1].split("</section>", 1)[0]
    assert phase.index('id="report-catalog-panel"') < phase.index(
        'id="report-preview-panel"'
    )
    for static_node in (
        _REPORTS_LAYOUT,
        _REPORT_CATALOG,
        _REPORT_LIST,
        _REPORT_PREVIEW,
    ):
        _assert_static_css_node(phase, static_node)

    desktop_width = 1200
    mobile_width = 768
    _assert_effective_css_declarations(
        css,
        ".reports-layout",
        desktop_width,
        {
            "display": "grid",
            "grid-template-columns": "minmax(0, 1fr)",
            "gap": "20px",
            "align-items": "start",
        },
    )
    _assert_effective_css_declarations(
        css,
        ".report-list",
        desktop_width,
        {
            "display": "flex",
            "gap": "12px",
            "max-width": "100%",
            "overflow-x": "auto",
            "overflow-y": "hidden",
            "padding": "4px 4px 10px",
            "scroll-snap-type": "x proximity",
            "scrollbar-gutter": "stable",
        },
    )
    _assert_effective_css_declarations(
        css,
        ".report-item",
        desktop_width,
        {
            "flex": "0 0 clamp(240px, 28vw, 340px)",
            "min-width": "0",
            "scroll-snap-align": "start",
        },
    )
    _assert_effective_css_declarations(
        css,
        ".report-preview-column",
        desktop_width,
        {"position": "static", "width": "100%"},
    )
    preview = _effective_css_declarations(
        css,
        ".report-preview-column",
        desktop_width,
    )
    assert preview["position"] != "sticky"

    _assert_effective_css_declarations(
        css,
        ".report-list",
        mobile_width,
        {
            "display": "grid",
            "grid-template-columns": "minmax(0, 1fr)",
            "overflow-x": "visible",
            "overflow-y": "visible",
            "padding-inline": "0",
            "scroll-snap-type": "none",
        },
    )
    _assert_effective_css_declarations(
        css,
        ".report-item",
        mobile_width,
        {"width": "100%", "max-width": "100%"},
    )
    assert re.search(r"\.report-item:focus-visible\s*\{[^}]*outline", css, re.S)
    reduced_motion_block = css.split("@media (prefers-reduced-motion: reduce)", 1)[1].split(
        "}", 1
    )[0]
    assert "transition-duration" in reduced_motion_block
    assert "scroll-behavior: auto" in reduced_motion_block


def test_display_score_formatter_uses_at_most_three_fraction_digits() -> None:
    script = f"""
const fs = require('fs');
const vm = require('vm');
global.window = {{}};
global.document = {{querySelector() {{ return null; }}}};
vm.runInThisContext(fs.readFileSync({json.dumps(str(RENDER_JS))}, 'utf8'));
const format = window.MorphicWorkbenchFormatDisplayScore;
if (typeof format !== 'function') process.exit(2);
console.log(JSON.stringify({{
  formatted: [format(1.23456), format(1.2), format(0), format(null), format('not-a-number')],
  rounded: window.MorphicWorkbenchRoundScoresForDisplay({{score: 1.23456, scores: [1.23456, 2.34567], nested: {{entropy_score: 0.98765, value: 9.87654}}}}),
}}));
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["formatted"] == ["1,235", "1,2", "0", "-", "-"]
    assert payload["rounded"] == {
        "score": 1.235,
        "scores": [1.235, 2.346],
        "nested": {"entropy_score": 0.988, "value": 9.87654},
    }


def test_profile_and_entropy_choices_explain_each_option_in_plain_language() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    app_source = APP_JS.read_text(encoding="utf-8")

    for value in (
        "phase1-default",
        "personal-balanced",
        "personal-focused",
        "legacy",
        "enhanced",
        "hybrid",
    ):
        option = html.split(f'value="{value}"', 1)[1].split("</option>", 1)[0]
        assert "data-hint=" in option
    wire_block = app_source.split("function wireChoiceCards", 1)[1].split(
        "function wireSolfeggioChoiceCards", 1
    )[0]
    assert "opt.dataset.hint" in wire_block


def test_report_preview_has_explicit_loading_error_and_file_states() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    app_source = APP_JS.read_text(encoding="utf-8")
    preview_block = app_source.split("function renderReportPreviewLoading", 1)[1].split(
        "async function loadReports", 1
    )[0]

    assert 'id="report-preview-state"' in html
    assert 'view?.mode === "file"' in preview_block
    assert "PDF-Datei" in preview_block
    assert "showReportPreviewState" in preview_block
    iframe = html.split('id="report-preview-frame"', 1)[1].split(">", 1)[0]
    assert "sandbox" in iframe
    assert 'title="Berichtsvorschau"' in iframe


def test_hardware_and_review_have_truthful_emf_and_scan_scope_surfaces() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    render_source = RENDER_JS.read_text(encoding="utf-8")

    assert 'id="review-scan-scope"' in html
    assert "emf-index-gauge" in render_source
    assert "EMF-Telemetrie deaktiviert" in render_source
    assert "scanProfileCatalog" in render_source


def test_hardware_phase_exposes_explicit_emf_telemetry_controls() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    api_source = (ROOT / "apps" / "web" / "static" / "workbench-api.js").read_text(
        encoding="utf-8"
    )
    app_source = APP_JS.read_text(encoding="utf-8")

    hardware_phase = html.split('id="hardware-phase"', 1)[1].split(
        '<!-- Phase 6:', 1
    )[0]
    assert 'id="emf-telemetry-state"' in hardware_phase
    assert 'id="emf-enable-button"' in hardware_phase
    assert 'id="emf-disable-button"' in hardware_phase
    assert 'aria-describedby="emf-help"' in hardware_phase
    assert "bewusst aktivierbar" in hardware_phase
    assert "derzeit keine Aktivierung in der Workbench" not in hardware_phase
    assert "loadEmfStatus" in api_source
    assert "enableEmfTelemetry" in api_source
    assert "disableEmfTelemetry" in api_source
    assert "wireEmfTelemetryControls" in app_source


def test_results_phase_header_has_spacing_and_accessibility_contract() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")

    results_phase = html.split('id="results-phase"', 1)[1].split(
        '<!-- Phase 9:', 1
    )[0]
    assert 'aria-labelledby="results-phase-title"' in results_phase
    assert 'aria-describedby="results-phase-subtitle"' in results_phase
    assert 'id="results-phase-title"' in results_phase
    assert 'id="results-phase-subtitle"' in results_phase
    assert 'class="results-heading-copy"' in results_phase
    assert "#results-phase .results-heading-copy" in css
    assert "#results-phase .step-subtitle" in css


def test_overflow_contract_covers_nested_grid_and_long_operator_values() -> None:
    css = APP_CSS.read_text(encoding="utf-8")
    assert ".panel > *" in css and "min-width: 0" in css
    assert ".review-card dd" in css and "overflow-wrap: anywhere" in css
    assert ".hardware-card-header" in css and "flex-wrap: wrap" in css
    assert ".report-preview-frame" in css and "max-width: 100%" in css


def test_gate4_report_catalog_precedes_full_width_nonsticky_preview() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")

    _assert_gate4_report_layout_contract(html, css)


def test_gate4_report_layout_contract_rejects_scoped_mutations() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")

    mutated_html = html.replace('role="toolbar"', 'role="group"', 1)
    desktop_list = _css_blocks(css, ".report-list")[0]
    mutated_desktop_css = _replace_css_declaration(
        css,
        desktop_list,
        "overflow-x: auto;",
        "overflow-x: clip;",
    )
    mobile_list = _css_blocks(css, ".report-list")[1]
    mutated_mobile_css = _replace_css_declaration(
        css,
        mobile_list,
        "overflow-x: visible;",
        "overflow-x: clip;",
    )
    appended_desktop_list_css = (
        css + "\n.report-list { overflow-x: visible; }\n"
    )
    appended_id_list_css = css + "\n#report-list { overflow-x: visible; }\n"
    appended_preview_css = (
        css + "\n.report-preview-column { position: sticky; }\n"
    )
    appended_mobile_css = css + (
        "\n@media (max-width: 768px) {\n"
        "  .report-list { overflow-x: auto; }\n"
        "}\n"
    )

    for mutated_source in (
        (mutated_html, css),
        (html, mutated_desktop_css),
        (html, mutated_mobile_css),
        (html, appended_desktop_list_css),
        (html, appended_id_list_css),
        (html, appended_preview_css),
        (html, appended_mobile_css),
    ):
        with pytest.raises(AssertionError):
            _assert_gate4_report_layout_contract(*mutated_source)


def test_gate4_report_layout_contract_matches_report_client_ancestor() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    mutated_css = css + (
        "\n.report-client-group .report-item { flex: 1 1 auto; }\n"
    )

    with pytest.raises(AssertionError):
        _assert_gate4_report_layout_contract(html, mutated_css)


def test_gate4_report_layout_contract_matches_labelled_catalog_ancestor() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    mutated_css = css + (
        '\n[aria-labelledby="reports-heading"] .report-list '
        "{ overflow-x: visible; }\n"
    )

    with pytest.raises(AssertionError):
        _assert_gate4_report_layout_contract(html, mutated_css)


@pytest.mark.parametrize(
    "override",
    (
        "#report-list { overflow-x: visible }",
        "#report-list { color: red; overflow-x: visible; }",
    ),
    ids=("final-declaration-without-semicolon", "same-line-declarations"),
)
def test_gate4_report_layout_contract_parses_valid_declaration_overrides(
    override: str,
) -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")

    with pytest.raises(AssertionError):
        _assert_gate4_report_layout_contract(html, css + f"\n{override}\n")


def test_gate4_report_layout_contract_ignores_print_media_on_screen() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    print_css = css + (
        "\n@media print and (max-width: 768px) {\n"
        "  #report-list { overflow-x: auto; }\n"
        "}\n"
    )

    _assert_gate4_report_layout_contract(html, print_css)


def test_gate4_report_layout_contract_negates_entire_media_query() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    not_print_css = css + (
        "\n@media not print and (max-width: 768px) {\n"
        "  #report-list { overflow-x: visible; }\n"
        "}\n"
    )

    with pytest.raises(AssertionError):
        _assert_gate4_report_layout_contract(html, not_print_css)


def test_gate4_report_layout_contract_expands_overflow_shorthand() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    shorthand_css = css + (
        "\n#report-list { overflow: visible !important; }\n"
    )

    with pytest.raises(AssertionError):
        _assert_gate4_report_layout_contract(html, shorthand_css)


def test_gate4_report_layout_contract_finds_adjacent_inline_rule() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    adjacent_rule_css = css + (
        "\n.unrelated { color: red; } "
        "#report-list { overflow-x: visible; }\n"
    )

    with pytest.raises(AssertionError):
        _assert_gate4_report_layout_contract(html, adjacent_rule_css)


def test_gate4_report_layout_contract_rejects_static_target_drift() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    mutated_html = html.replace(
        'class="reports-layout"',
        'class="reports-layout-broken"',
        1,
    )

    with pytest.raises(AssertionError):
        _assert_gate4_report_layout_contract(mutated_html, css)


def test_gate4_report_layout_contract_parses_spaced_important_suffix() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    spaced_important_css = css + (
        "\n@media (min-width: 769px) {\n"
        "  #report-list { overflow-x: visible ! important; }\n"
        "  #report-list { overflow-x: auto; }\n"
        "}\n"
    )

    with pytest.raises(AssertionError):
        _assert_gate4_report_layout_contract(html, spaced_important_css)
