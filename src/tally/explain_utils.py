"""
Utilities for explaining rule patterns and view filters in human-readable form.
"""

import re


def explain_pattern(pattern: str) -> str:
    """Convert a regex/expression pattern to human-readable explanation."""
    if not pattern:
        return ''

    lowered = pattern.lower()

    # Handle expression-style patterns (contains, startswith, etc.)
    if 'contains(' in lowered:
        match = re.search(r'contains\(["\']([^"\']+)["\']\)', pattern, re.IGNORECASE)
        if match:
            return f'Description contains "{match.group(1)}"'

    if 'startswith(' in lowered:
        match = re.search(r'startswith\(["\']([^"\']+)["\']\)', pattern, re.IGNORECASE)
        if match:
            return f'Description starts with "{match.group(1)}"'

    if 'anyof(' in lowered:
        match = re.search(r'anyof\(([^)]+)\)', pattern, re.IGNORECASE)
        if match:
            terms = [t.strip().strip('"\'') for t in match.group(1).split(',')]
            if len(terms) <= 3:
                return f'Description contains any of: {", ".join(terms)}'
            return f'Description contains any of: {", ".join(terms[:3])}...'

    # Handle regex patterns
    parts = []

    # Check for alternation (OR)
    if '|' in pattern and not pattern.startswith('('):
        alternatives = pattern.split('|')
        if len(alternatives) <= 3:
            terms = [a.replace('.*', ' ... ').replace('\\s', ' ').strip() for a in alternatives]
            return f'Matches: {" OR ".join(terms)}'
        terms = [a.replace('.*', ' ... ').replace('\\s', ' ').strip() for a in alternatives[:3]]
        return f'Matches: {" OR ".join(terms)} (+ {len(alternatives) - 3} more)'

    # Check for start anchor
    if pattern.startswith('^'):
        pattern = pattern[1:]
        parts.append('Starts with')
    else:
        parts.append('Contains')

    # Check for end anchor
    end_anchor = pattern.endswith('$')
    if end_anchor:
        pattern = pattern[:-1]

    # Clean up common regex syntax for display
    display = pattern
    display = display.replace('.*', ' ... ')
    display = display.replace('.+', ' ... ')
    display = display.replace('\\s+', ' ')
    display = display.replace('\\s', ' ')
    display = display.replace('\\d+', '#')
    display = display.replace('\\d', '#')
    display = display.replace('(?!', ' (not followed by ')
    display = display.replace('(?:', '(')
    display = display.replace(')', ')')

    parts.append(f'"{display.strip()}"')

    if end_anchor:
        parts.append('at end')

    return ' '.join(parts)


def explain_view_filter(filter_expr: str) -> str:
    """Convert a view filter expression to human-readable explanation."""
    if not filter_expr:
        return ''

    explanations = []
    lowered = filter_expr.lower()

    # Parse common conditions
    if 'category ==' in lowered or "category='" in lowered:
        match = re.search(r'category\s*==?\s*["\']([^"\']+)["\']', filter_expr, re.IGNORECASE)
        if match:
            explanations.append(f'Category is "{match.group(1)}"')

    if 'subcategory ==' in lowered or "subcategory='" in lowered:
        match = re.search(r'subcategory\s*==?\s*["\']([^"\']+)["\']', filter_expr, re.IGNORECASE)
        if match:
            explanations.append(f'Subcategory is "{match.group(1)}"')

    if 'tag(' in lowered or 'has_tag(' in lowered:
        matches = re.findall(r'(?:tag|has_tag)\(["\']([^"\']+)["\']\)', filter_expr, re.IGNORECASE)
        for tag in matches:
            explanations.append(f'Has tag "{tag}"')

    if 'months >' in filter_expr or 'months>=' in filter_expr:
        match = re.search(r'months\s*>=?\s*(\d+)', filter_expr)
        if match:
            explanations.append(f'Active {match.group(1)}+ months')

    if 'total >' in filter_expr or 'total>=' in filter_expr:
        match = re.search(r'total\s*>=?\s*(\d+)', filter_expr)
        if match:
            explanations.append(f'Total ≥ ${match.group(1)}')

    if 'cv <' in filter_expr or 'cv<=' in filter_expr:
        match = re.search(r'cv\s*<=?\s*([\d.]+)', filter_expr)
        if match:
            explanations.append(f'Coefficient of variation ≤ {match.group(1)}')

    # Join explanations or fallback to raw expression
    if explanations:
        return ' AND '.join(explanations)

    return filter_expr.replace('==', '=').replace('&&', ' and ').replace('||', ' or ')
