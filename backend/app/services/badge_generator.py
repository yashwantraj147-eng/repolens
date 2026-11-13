"""Dynamic SVG badge generator for repository health scores.

Produces Shields.io-compatible vector SVG badges that maintainers can embed
directly into their GitHub READMEs.
"""

from typing import Optional


def get_grade_color(grade: str) -> str:
    """Return an accessible hex color for a health grade.

    Args:
        grade: Letter grade (e.g. 'A+', 'B', 'C-', 'F').

    Returns:
        Hex color code string.
    """
    normalized = grade.upper().strip()
    if normalized in ("A+", "A"):
        return "#2ea44f"  # GitHub green
    elif normalized in ("A-", "B+", "B"):
        return "#0969da"  # GitHub blue
    elif normalized in ("B-", "C+"):
        return "#8250df"  # GitHub purple
    elif normalized in ("C", "C-"):
        return "#d29922"  # GitHub amber
    elif normalized in ("D", "F"):
        return "#cf222e"  # GitHub red
    return "#6e7681"  # Neutral gray


def _estimate_text_width(text: str, font_size: int = 11) -> int:
    """Estimate visual text width in pixels for Arial/Verdana sans-serif fonts.

    Args:
        text: String to measure.
        font_size: Font size in pixels.

    Returns:
        Width in pixels.
    """
    scale = font_size / 11.0
    char_widths = {
        "i": 3.5, "l": 3.5, "I": 4.0, "j": 4.5, "t": 5.0, "f": 5.0, "r": 5.0,
        "m": 10.0, "w": 9.5, "M": 10.5, "W": 11.0,
        ".": 3.5, "/": 5.5, "+": 7.0, "-": 5.5, "%": 10.0,
    }
    total = 0.0
    for ch in text:
        total += char_widths.get(ch, 7.0)
    return int(total * scale)


def generate_badge_svg(
    label: str = "repolens",
    value: str = "95/100 · A+",
    grade: str = "A+",
    style: str = "flat",
) -> str:
    """Generate a clean, high-DPI SVG badge.

    Args:
        label: Left badge label (default 'repolens').
        value: Right badge value (e.g. '92/100 · A+').
        grade: Grade for color selection.
        style: Badge visual style ('flat', 'flat-square', 'for-the-badge').

    Returns:
        Complete SVG markup string.
    """
    color = get_grade_color(grade)
    is_square = style == "flat-square"
    is_bold = style == "for-the-badge"

    font_size = 10 if is_bold else 11
    height = 28 if is_bold else 20
    radius = 0 if is_square else (4 if is_bold else 3)
    text_y = 19 if is_bold else 14
    shadow_y = 20 if is_bold else 15

    display_label = label.upper() if is_bold else label
    display_value = value.upper() if is_bold else value

    # Calculate widths
    padding = 10 if is_bold else 8
    icon_width = 16  # width for search lens icon + spacing
    label_text_width = _estimate_text_width(display_label, font_size)
    value_text_width = _estimate_text_width(display_value, font_size)

    left_width = icon_width + label_text_width + (padding * 2)
    right_width = value_text_width + (padding * 2)
    total_width = left_width + right_width

    label_center_x = (icon_width + left_width) / 2
    value_center_x = left_width + (right_width / 2)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{height}" viewBox="0 0 {total_width} {height}" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="{height}" rx="{radius}" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{left_width}" height="{height}" fill="#161b22"/>
    <rect x="{left_width}" width="{right_width}" height="{height}" fill="{color}"/>
    <rect width="{total_width}" height="{height}" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="{font_size}" font-weight="{'700' if is_bold else '600'}">
    <!-- Search Lens Icon -->
    <g transform="translate(7, {(height - 12) / 2}) scale(0.75)" fill="none" stroke="#58a6ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="7" cy="7" r="5"/>
      <line x1="11" y1="11" x2="15" y2="15"/>
    </g>
    <!-- Label Text -->
    <text x="{label_center_x}" y="{shadow_y}" fill="#010101" fill-opacity=".3">{display_label}</text>
    <text x="{label_center_x}" y="{text_y}" fill="#f0f6fc">{display_label}</text>
    <!-- Value Text -->
    <text x="{value_center_x}" y="{shadow_y}" fill="#010101" fill-opacity=".3">{display_value}</text>
    <text x="{value_center_x}" y="{text_y}" fill="#fff">{display_value}</text>
  </g>
</svg>"""

    return svg.strip()

