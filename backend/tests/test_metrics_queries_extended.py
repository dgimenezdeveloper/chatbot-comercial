"""Tests for the 7 newly optimized metrics functions (chatbot-mvp-completion).

Covers: get_conversion_by_service, get_avg_modification_time,
get_avg_reminder_response_time, get_avg_time_between_first_second,
get_read_receipt_buckets, get_nps, get_response_speed_percentiles.
"""

from unittest.mock import MagicMock

import pytest

from app.services.metrics_queries import (
    get_avg_modification_time,
    get_avg_reminder_response_time,
    get_avg_time_between_first_second,
    get_conversion_by_service,
    get_nps,
    get_read_receipt_buckets,
    get_response_speed_percentiles,
)


# ============================================================================
# Shared helpers
# ============================================================================

def mock_scalar_sequence(db, *values):
    """Chain db.query().filter().scalar() to return values in order."""
    scalars = iter(values)

    def side_effect():
        return next(scalars)

    db.query.return_value.filter.return_value.scalar.side_effect = side_effect
    return db


def mock_scalar_return(db, value):
    """Return always the same scalar value."""
    db.query.return_value.filter.return_value.scalar.return_value = value
    return db


# ============================================================================
# C1.1 — get_conversion_by_service
# ============================================================================

class TestConversionByService:
    """C1.1: Tasa de conversion por servicio — N+1 optimized."""

    def test_returns_services_dict(self, mock_db):
        """Services dict with service_id, appointments, queries, rate."""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            # appt_rows
            [MagicMock(service_id=1, appointments=10), MagicMock(service_id=2, appointments=5)],
            # query_rows
            [MagicMock(_astext="1", query_count=20), MagicMock(_astext="2", query_count=25)],
        ]
        result = get_conversion_by_service(mock_db, business_id=1, days=30)
        services = result["services"]
        assert len(services) == 2
        assert services[0]["service_id"] == 1
        assert services[0]["appointments"] == 10
        assert services[0]["queries"] == 20
        assert services[0]["rate"] == 50.0  # 10/20*100

    def test_overall_rate_calculation(self, mock_db):
        """overall_rate = sum(appointments) / sum(queries)."""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            [MagicMock(service_id=1, appointments=30)],
            [MagicMock(_astext="1", query_count=100)],
        ]
        result = get_conversion_by_service(mock_db, business_id=1)
        assert result["value"] == 30.0  # 30/100*100

    def test_division_by_zero_guard(self, mock_db):
        """When no queries, rate = 0.0."""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            [MagicMock(service_id=1, appointments=5)],
            [],  # no queries
        ]
        result = get_conversion_by_service(mock_db, business_id=1)
        assert result["services"][0]["rate"] == 0.0
        assert result["value"] == 0.0

    def test_empty_appointments(self, mock_db):
        """No appointments at all."""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            [],
            [],
        ]
        result = get_conversion_by_service(mock_db, business_id=1)
        assert result["services"] == []
        assert result["value"] == 0.0

    def test_overall_rate_zero_queries_all_services(self, mock_db):
        """All services have 0 queries → overall_rate = 0.0."""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            [MagicMock(service_id=1, appointments=10), MagicMock(service_id=2, appointments=20)],
            [],  # 0 queries for any service
        ]
        result = get_conversion_by_service(mock_db, business_id=1)
        assert result["value"] == 0.0

    def test_period_in_result(self, mock_db):
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            [],
            [],
        ]
        result = get_conversion_by_service(mock_db, business_id=1, days=7)
        assert result["period"] == "7d"


# ============================================================================
# C2.4 — get_avg_modification_time
# ============================================================================

class TestAvgModificationTime:
    """C2.4: Average time between original appointment and modification (hours)."""

    def test_returns_avg_hours(self, mock_db):
        """Two modifications, bulks pre-fetched correctly."""
        t1 = MagicMock()  # modification time
        t2 = MagicMock()
        o1 = MagicMock()  # original created_at
        o2 = MagicMock()
        # 2 hours = 7200s, 3 hours = 10800s
        t1.__sub__ = lambda self, other: type("td", (), {"total_seconds": lambda: 7200.0})()
        t2.__sub__ = lambda self, other: type("td", (), {"total_seconds": lambda: 10800.0})()

        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            # Modifications: 2 rows
            [MagicMock(aid=10, mod_time=t1), MagicMock(aid=20, mod_time=t2)],
            # Bulk pre-fetch: 2 originals
            [MagicMock(id=10, created_at=o1), MagicMock(id=20, created_at=o2)],
        ]
        result = get_avg_modification_time(mock_db, business_id=1)
        assert result["avg_hours"] == 2.5  # (2+3)/2

    def test_zero_when_no_modifications(self, mock_db):
        """Empty rows returns avg_hours=0."""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []
        result = get_avg_modification_time(mock_db, business_id=1)
        assert result["avg_hours"] == 0.0
        assert result["value"] == 0.0

    def test_bulk_pre_fetch_works(self, mock_db):
        """Only fetches original appointments matching modification IDs."""
        t = MagicMock()
        t.__sub__ = lambda self, other: type("td", (), {"total_seconds": lambda: 3600.0})()
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            [MagicMock(aid=5, mod_time=t)],
            [MagicMock(id=5, created_at=MagicMock())],
        ]
        result = get_avg_modification_time(mock_db, business_id=1)
        assert result["avg_hours"] == 1.0

    def test_missing_original_skipped(self, mock_db):
        """When original not found, count stays 0."""
        t = MagicMock()
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            [MagicMock(aid=99, mod_time=t)],
            [],  # No originals found
        ]
        result = get_avg_modification_time(mock_db, business_id=1)
        assert result["avg_hours"] == 0.0  # count=0 → avg = 0

    def test_custom_days(self, mock_db):
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []
        result = get_avg_modification_time(mock_db, business_id=1, days=7)
        assert result["period"] == "7d"


# ============================================================================
# C4.4 — get_avg_reminder_response_time
# ============================================================================

class TestAvgReminderResponseTime:
    """C4.4: Average reminder response time in minutes — N+1 optimized."""

    def test_returns_avg_minutes(self, mock_db):
        """Two reminders, each with a response."""
        rem_t = MagicMock()
        resp_t1 = MagicMock()
        resp_t2 = MagicMock()
        # response 300s later and 900s later
        resp_t1.__gt__ = lambda s, o: True
        resp_t2.__gt__ = lambda s, o: True
        resp_t1.__sub__ = lambda s, o: type("td", (), {"total_seconds": lambda: 300.0})()
        resp_t2.__sub__ = lambda s, o: type("td", (), {"total_seconds": lambda: 900.0})()

        mock_db.query.return_value.filter.return_value.all.side_effect = [
            # Reminders
            [MagicMock(session_id="s1", timestamp=rem_t), MagicMock(session_id="s2", timestamp=rem_t)],
            # Responses
            [MagicMock(session_id="s1", first_resp=resp_t1), MagicMock(session_id="s2", first_resp=resp_t2)],
        ]
        result = get_avg_reminder_response_time(mock_db, business_id=1)
        assert result["avg_minutes"] == 10.0  # (300+900)/2/60 = 10.0
        assert result["total_reminders"] == 2

    def test_zero_when_no_reminders(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        result = get_avg_reminder_response_time(mock_db, business_id=1)
        assert result["avg_minutes"] == 0.0
        assert result["total_reminders"] == 0
        assert result["value"] == 0.0

    def test_reminders_with_no_responses(self, mock_db):
        """When there are no responses, avg remains 0."""
        mock_db.query.return_value.filter.return_value.all.side_effect = [
            [MagicMock(session_id="s1", timestamp=MagicMock())],
            [],  # No responses
        ]
        result = get_avg_reminder_response_time(mock_db, business_id=1)
        assert result["avg_minutes"] == 0.0

    def test_skips_response_before_reminder(self, mock_db):
        """If response_time <= reminder_time, it's skipped."""
        rem_t = MagicMock()
        resp_t = MagicMock()
        resp_t.__gt__ = lambda s, o: False  # not greater

        mock_db.query.return_value.filter.return_value.all.side_effect = [
            [MagicMock(session_id="s1", timestamp=rem_t)],
            [MagicMock(session_id="s1", first_resp=resp_t)],
        ]
        result = get_avg_reminder_response_time(mock_db, business_id=1)
        assert result["avg_minutes"] == 0.0  # Skipped → count=0

    def test_custom_days(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        result = get_avg_reminder_response_time(mock_db, business_id=1, days=7)
        assert result["period"] == "7d"


# ============================================================================
# C6.4 — get_avg_time_between_first_second
# ============================================================================

class TestAvgTimeBetweenFirstSecond:
    """C6.4: Average time between 1st and 2nd appointment (CTE + ROW_NUMBER)."""

    def test_returns_avg_days(self, mock_db):
        """Two users, each with two appointments. Delta: 5 days and 10 days."""
        mock_db.query.return_value.filter.return_value.cte.return_value = MagicMock()
        cte_mock = mock_db.query.return_value.filter.return_value.cte.return_value
        cte_mock.c.user_id = MagicMock()
        cte_mock.c.rn = MagicMock()
        cte_mock.c.created_at = MagicMock()

        mock_db.query.return_value.filter.return_value.group_by.return_value.having.return_value.all.return_value = [
            MagicMock(user_id=1, first_date=type("dt", (), {"__sub__": lambda s, o: type("td", (), {"days": 5})()})(), second_date=MagicMock()),
            MagicMock(user_id=2, first_date=type("dt", (), {"__sub__": lambda s, o: type("td", (), {"days": 10})()})(), second_date=MagicMock()),
        ]
        result = get_avg_time_between_first_second(mock_db, business_id=1)
        assert result["avg_days"] == 7.5  # (5+10)/2

    def test_no_pairs_returns_zero(self, mock_db):
        """No users with 2 appointments in period."""
        mock_db.query.return_value.filter.return_value.cte.return_value = MagicMock()
        mock_db.query.return_value.filter.return_value.group_by.return_value.having.return_value.all.return_value = []
        result = get_avg_time_between_first_second(mock_db, business_id=1)
        assert result["avg_days"] == 0.0
        assert result["value"] == 0.0

    def test_single_user_two_appointments(self, mock_db):
        """CTE with ROW_NUMBER properly partitions by user_id."""
        mock_db.query.return_value.filter.return_value.cte.return_value = MagicMock()
        mock_db.query.return_value.filter.return_value.group_by.return_value.having.return_value.all.return_value = [
            MagicMock(user_id=1,
                      first_date=type("dt", (), {"__sub__": lambda s, o: type("td", (), {"days": 3})()})(),
                      second_date=MagicMock()),
        ]
        result = get_avg_time_between_first_second(mock_db, business_id=1)
        assert result["avg_days"] == 3.0

    def test_custom_days(self, mock_db):
        mock_db.query.return_value.filter.return_value.cte.return_value = MagicMock()
        mock_db.query.return_value.filter.return_value.group_by.return_value.having.return_value.all.return_value = []
        result = get_avg_time_between_first_second(mock_db, business_id=1, days=60)
        assert result["period"] == "60d"


# ============================================================================
# C8.6 — get_read_receipt_buckets
# ============================================================================

class TestReadReceiptBuckets:
    """C8.6: Read receipt buckets (mutually exclusive: if/elif/else)."""

    def test_buckets_mutually_exclusive(self, mock_db):
        """1h bucket should not also appear in 4h or 24h. Uses elif."""
        rem_t = MagicMock()
        read_30m = MagicMock()   # 0.5h → 1h bucket
        read_3h = MagicMock()    # 3h → 4h bucket
        read_12h = MagicMock()   # 12h → 24h bucket

        read_30m.__gt__ = lambda s, o: True
        read_3h.__gt__ = lambda s, o: True
        read_12h.__gt__ = lambda s, o: True
        read_30m.__sub__ = lambda s, o: type("td", (), {"total_seconds": lambda: 0.5 * 3600})()
        read_3h.__sub__ = lambda s, o: type("td", (), {"total_seconds": lambda: 3.0 * 3600})()
        read_12h.__sub__ = lambda s, o: type("td", (), {"total_seconds": lambda: 12.0 * 3600})()

        mock_db.query.return_value.filter.return_value.all.side_effect = [
            # reminders
            [
                MagicMock(session_id="s1", timestamp=rem_t),
                MagicMock(session_id="s2", timestamp=rem_t),
                MagicMock(session_id="s3", timestamp=rem_t),
            ],
            # reads
            [
                MagicMock(session_id="s1", first_read=read_30m),
                MagicMock(session_id="s2", first_read=read_3h),
                MagicMock(session_id="s3", first_read=read_12h),
            ],
        ]
        result = get_read_receipt_buckets(mock_db, business_id=1)
        buckets = result["buckets"]
        assert buckets["1h"]["count"] == 1
        assert buckets["4h"]["count"] == 1
        assert buckets["24h"]["count"] == 1
        assert result["total_reminders"] == 3

    def test_percentages_sum(self, mock_db):
        """Percentages are per-bucket."""
        rem_t = MagicMock()
        read_t = MagicMock()
        read_t.__gt__ = lambda s, o: True
        read_t.__sub__ = lambda s, o: type("td", (), {"total_seconds": lambda: 0.2 * 3600})()

        mock_db.query.return_value.filter.return_value.all.side_effect = [
            [MagicMock(session_id="s1", timestamp=rem_t)],
            [MagicMock(session_id="s1", first_read=read_t)],
        ]
        result = get_read_receipt_buckets(mock_db, business_id=1)
        assert result["buckets"]["1h"]["pct"] == 100.0
        assert result["buckets"]["4h"]["pct"] == 0.0
        assert result["buckets"]["24h"]["pct"] == 0.0

    def test_empty_reminders(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        result = get_read_receipt_buckets(mock_db, business_id=1)
        assert result["total_reminders"] == 0
        assert result["buckets"]["1h"]["count"] == 0
        assert result["buckets"]["4h"]["count"] == 0
        assert result["buckets"]["24h"]["count"] == 0

    def test_value_is_1h_percentage(self, mock_db):
        """value is the 1h bucket pct."""
        mock_db.query.return_value.filter.return_value.all.return_value = []
        result = get_read_receipt_buckets(mock_db, business_id=1)
        assert result["value"] == 0.0

    def test_no_reads_but_reminders_exist(self, mock_db):
        """Reminders sent but no reads → all buckets 0."""
        mock_db.query.return_value.filter.return_value.all.side_effect = [
            [MagicMock(session_id="s1", timestamp=MagicMock())],
            [],  # No reads
        ]
        result = get_read_receipt_buckets(mock_db, business_id=1)
        assert result["total_reminders"] == 1
        assert result["buckets"]["1h"]["count"] == 0


# ============================================================================
# C9.2 — get_nps
# ============================================================================

class TestNPS:
    """C9.2: Net Promoter Score — scale 1-5, promoters >= 5, detractors <= 3."""

    def test_nps_calculation(self, mock_db):
        """12 total: 6 promoters, 2 detractors, 4 passives → NPS = (6-2)/12*100 = 33.3."""
        mock_scalar_sequence(mock_db, 12, 6, 2)
        result = get_nps(mock_db, business_id=1)
        assert result["promoters"] == 6
        assert result["detractors"] == 2
        assert result["passives"] == 4  # 12-6-2
        assert result["total"] == 12
        assert round(result["value"], 1) == round((6 - 2) / 12 * 100, 1)

    def test_scale_1_to_5(self, mock_db):
        """Verifies: promoters >= 5 (not 9), detractors <= 3 (not 6)."""
        # 5 total: 2x score=5 (promoters), 1x score=3 (detractor), 1x score=4 (passive), 1x score=1 (detractor)
        mock_scalar_sequence(mock_db, 5, 2, 2)
        result = get_nps(mock_db, business_id=1)
        assert result["passives"] == 1  # 5-2-2
        assert result["value"] == 0.0  # (2-2)/5*100 = 0.0

    def test_zero_feedbacks(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0, 0)
        result = get_nps(mock_db, business_id=1)
        assert result["value"] == 0.0
        assert result["promoters"] == 0
        assert result["detractors"] == 0
        assert result["passives"] == 0

    def test_all_promoters(self, mock_db):
        """All scores >= 5 → NPS = 100."""
        mock_scalar_sequence(mock_db, 10, 10, 0)
        result = get_nps(mock_db, business_id=1)
        assert result["value"] == 100.0
        assert result["passives"] == 0

    def test_all_detractors(self, mock_db):
        """All scores <= 3 → NPS = -100."""
        mock_scalar_sequence(mock_db, 5, 0, 5)
        result = get_nps(mock_db, business_id=1)
        assert result["value"] == -100.0
        assert result["passives"] == 0

    def test_status_uses_nps_entry(self, mock_db):
        """_status uses 'nps' metric_name (not 'reminder_confirmation_rate')."""
        mock_scalar_sequence(mock_db, 10, 8, 1)  # (8-1)/10*100 = 70 → ok (>50)
        result = get_nps(mock_db, business_id=1)
        assert "status" in result
        # NPS thresholds: warning=50, critical=0
        assert result["status"] == "ok"  # 70 > 50


# ============================================================================
# C8.3 — get_response_speed_percentiles
# ============================================================================

class TestResponseSpeedPercentiles:
    """C8.3: Response speed P50 and P95 using percentile_cont."""

    def test_returns_p50_and_p95(self, mock_db):
        """Both percentiles returned as float."""
        mock_db.query.return_value.filter.return_value.subquery.return_value = MagicMock()
        # Configure two separate scalar calls for p50 and p95
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [1.5, 8.2]
        result = get_response_speed_percentiles(mock_db, business_id=1)
        assert result["p50_seconds"] == 1.5
        assert result["p95_seconds"] == 8.2
        assert result["value"] == 1.5  # value = p50

    def test_none_scalar_falls_back_to_zero(self, mock_db):
        """When percentile_cont returns None, fallback to 0.0."""
        mock_db.query.return_value.filter.return_value.subquery.return_value = MagicMock()
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [None, None]
        result = get_response_speed_percentiles(mock_db, business_id=1)
        assert result["p50_seconds"] == 0.0
        assert result["p95_seconds"] == 0.0

    def test_custom_days(self, mock_db):
        mock_db.query.return_value.filter.return_value.subquery.return_value = MagicMock()
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [2.0, 10.0]
        result = get_response_speed_percentiles(mock_db, business_id=1, days=14)
        assert result["period"] == "14d"

    def test_percentile_cont_within_group_used(self, mock_db):
        """Verifies the subquery + percentile_cont approach is used."""
        mock_db.query.return_value.filter.return_value.subquery.return_value = MagicMock()
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [3.0, 12.0]
        result = get_response_speed_percentiles(mock_db, business_id=1)
        assert isinstance(result["p50_seconds"], float)
        assert isinstance(result["p95_seconds"], float)
        assert result["threshold"] is None
        assert result["status"] == "ok"

    def test_zero_when_one_event(self, mock_db):
        """With a single event, gap is NULL, both percentiles are None."""
        mock_db.query.return_value.filter.return_value.subquery.return_value = MagicMock()
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [None, None]
        result = get_response_speed_percentiles(mock_db, business_id=1)
        assert result["p50_seconds"] == 0.0
        assert result["p95_seconds"] == 0.0
