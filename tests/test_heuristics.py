from backend.pipeline.heuristics import (
    TimelinePoint,
    build_events_from_kill_feed,
    detect_cs_stall,
    detect_repeated_killer,
    parse_kill_feed_line,
)


def test_parse_kill_feed_line_kill():
    parsed = parse_kill_feed_line("Lee Sin killed Yasuo")
    assert parsed == {
        "event_type": "kill",
        "data_json": {"killer": "Lee Sin", "victim": "Yasuo"},
    }


def test_parse_kill_feed_line_objective():
    parsed = parse_kill_feed_line("Dragon slain by Team Red")
    assert parsed == {
        "event_type": "objective",
        "data_json": {"objective": "Dragon", "team": "Team Red"},
    }


def test_parse_kill_feed_line_unrecognized():
    assert parse_kill_feed_line("totalmente irrelevante") is None


def test_build_events_marks_player_deaths():
    lines = [(45, "Lee Sin killed Yasuo"), (60, "Yasuo killed Lux")]
    events = build_events_from_kill_feed(lines, player_name="Yasuo")

    assert events[0]["event_type"] == "death"
    assert events[0]["timestamp_seconds"] == 45
    assert events[1]["event_type"] == "kill"


def test_detect_repeated_killer_flags_pattern():
    events = [
        {"event_type": "death", "timestamp_seconds": 45, "data_json": {"killer": "Lee Sin", "victim": "Yasuo"}},
        {"event_type": "death", "timestamp_seconds": 320, "data_json": {"killer": "Lee Sin", "victim": "Yasuo"}},
        {"event_type": "death", "timestamp_seconds": 500, "data_json": {"killer": "Lux", "victim": "Yasuo"}},
    ]
    patterns = detect_repeated_killer(events, min_count=2)

    assert len(patterns) == 1
    assert patterns[0]["data_json"]["killer"] == "Lee Sin"
    assert patterns[0]["data_json"]["count"] == 2


def test_detect_cs_stall_finds_long_gap():
    timeline = [
        TimelinePoint(timestamp_seconds=0, cs=10, gold=500, level=1),
        TimelinePoint(timestamp_seconds=30, cs=15, gold=600, level=1),
        TimelinePoint(timestamp_seconds=150, cs=15, gold=600, level=1),  # 120s sem crescer
        TimelinePoint(timestamp_seconds=160, cs=20, gold=700, level=2),
    ]
    stalls = detect_cs_stall(timeline, threshold_seconds=90)

    assert len(stalls) == 1
    assert stalls[0]["data_json"]["duration_seconds"] == 120


def test_detect_cs_stall_ignores_short_gaps():
    timeline = [
        TimelinePoint(timestamp_seconds=0, cs=10, gold=500, level=1),
        TimelinePoint(timestamp_seconds=30, cs=15, gold=600, level=1),
        TimelinePoint(timestamp_seconds=60, cs=20, gold=700, level=1),
    ]
    assert detect_cs_stall(timeline, threshold_seconds=90) == []
