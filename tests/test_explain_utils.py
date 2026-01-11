from tally.explain_utils import explain_pattern, explain_view_filter


def test_explain_pattern_contains():
    assert explain_pattern('contains("NETFLIX")') == 'Description contains "NETFLIX"'


def test_explain_pattern_anyof_truncates():
    assert explain_pattern('anyof("A", "B", "C", "D")') == 'Description contains any of: A, B, C...'


def test_explain_pattern_regex_with_anchors():
    assert explain_pattern('^AMZN.*$') == 'Starts with "AMZN ..." at end'


def test_explain_view_filter_compose():
    expr = 'tag("business") && months >= 6 && total >= 1200 && cv <= 0.3'
    expected = 'Has tag "business" AND Active 6+ months AND Total ≥ $1200 AND Coefficient of variation ≤ 0.3'
    assert explain_view_filter(expr) == expected


def test_explain_view_filter_fallback():
    expr = 'amount > 10 && source == "Chase"'
    assert explain_view_filter(expr) == 'amount > 10  and  source = "Chase"'
