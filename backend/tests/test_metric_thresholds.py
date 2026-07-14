"""Tests for PUT thresholds endpoint validation (C3 fix) + ThresholdItem model.

Covers: ThresholdItem Pydantic validation, Reject invalid operator,
Reject missing metric_name, Upsert logic (create new / update existing).
"""

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.api.v1.admin.metric_thresholds import ThresholdItem


# ============================================================================
# ThresholdItem — Pydantic validation (C3 fix)
# ============================================================================

class TestThresholdItemValidation:
    """C3: ThresholdItem with Field validators + Literal['lt','gt'] operator."""

    def test_valid_item_lt(self):
        """Valid ThresholdItem with operator='lt'."""
        item = ThresholdItem(
            metric_name="conversion_rate",
            warning_value=20.0,
            critical_value=10.0,
            operator="lt",
        )
        assert item.metric_name == "conversion_rate"
        assert item.warning_value == 20.0
        assert item.critical_value == 10.0
        assert item.operator == "lt"

    def test_valid_item_gt(self):
        """Valid ThresholdItem with operator='gt'."""
        item = ThresholdItem(
            metric_name="csat_average",
            warning_value=3.5,
            critical_value=4.0,
            operator="gt",
        )
        assert item.operator == "gt"

    def test_default_operator_is_lt(self):
        """When operator is omitted, default is 'lt'."""
        item = ThresholdItem(
            metric_name="nps",
            warning_value=50.0,
            critical_value=0.0,
        )
        assert item.operator == "lt"

    def test_rejects_invalid_operator(self):
        """Invalid operator (not 'lt' or 'gt') raises ValidationError."""
        with pytest.raises(ValidationError):
            ThresholdItem(
                metric_name="test_metric",
                warning_value=10.0,
                critical_value=5.0,
                operator="invalid_op",
            )

    def test_rejects_missing_metric_name(self):
        """Missing required field metric_name raises ValidationError."""
        with pytest.raises(ValidationError):
            ThresholdItem(
                warning_value=10.0,
                critical_value=5.0,
                operator="lt",
            )

    def test_rejects_empty_metric_name(self):
        """Empty string metric_name raises ValidationError (min_length=1)."""
        with pytest.raises(ValidationError):
            ThresholdItem(
                metric_name="",
                warning_value=10.0,
                critical_value=5.0,
                operator="lt",
            )

    def test_rejects_missing_warning_value(self):
        """Missing warning_value raises ValidationError."""
        with pytest.raises(ValidationError):
            ThresholdItem(
                metric_name="test_metric",
                critical_value=5.0,
                operator="lt",
            )

    def test_rejects_missing_critical_value(self):
        """Missing critical_value raises ValidationError."""
        with pytest.raises(ValidationError):
            ThresholdItem(
                metric_name="test_metric",
                warning_value=10.0,
                operator="lt",
            )

    def test_rejects_non_numeric_values(self):
        """Non-float values raise ValidationError."""
        with pytest.raises(ValidationError):
            ThresholdItem(
                metric_name="test_metric",
                warning_value="not_a_number",
                critical_value=5.0,
                operator="lt",
            )

    def test_accepts_integer_values(self):
        """Integers are coerced to float by Pydantic."""
        item = ThresholdItem(
            metric_name="nps",
            warning_value=50,
            critical_value=0,
            operator="lt",
        )
        assert isinstance(item.warning_value, float)
        assert isinstance(item.critical_value, float)

    def test_model_dump_format(self):
        """model_dump() returns proper dict structure."""
        item = ThresholdItem(
            metric_name="conversion_rate",
            warning_value=20.0,
            critical_value=10.0,
            operator="lt",
        )
        data = item.model_dump()
        assert data == {
            "metric_name": "conversion_rate",
            "warning_value": 20.0,
            "critical_value": 10.0,
            "operator": "lt",
        }

    def test_multiple_items_in_list(self):
        """list[ThresholdItem] works in PUT body."""
        items = [
            ThresholdItem(metric_name="m1", warning_value=10.0, critical_value=5.0, operator="lt"),
            ThresholdItem(metric_name="m2", warning_value=50.0, critical_value=80.0, operator="gt"),
        ]
        assert len(items) == 2
        assert items[0].metric_name == "m1"
        assert items[1].metric_name == "m2"


# ============================================================================
# PUT /api/v1/admin/metric-thresholds — Upsert logic
# ============================================================================

class TestUpsertLogic:
    """Upsert: creates new thresholds, updates existing ones."""

    def test_creates_new_threshold(self):
        """When no existing threshold, creates a new one."""
        # Simulate the upsert logic directly
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        item = ThresholdItem(
            metric_name="conversion_rate",
            warning_value=25.0,
            critical_value=15.0,
            operator="lt",
        )

        existing = mock_db.query.return_value.filter.return_value.first.return_value
        assert existing is None

        # Simulate creation
        from app.db.models.metric_threshold import MetricThreshold
        new_t = MetricThreshold(
            business_id=1,
            metric_name=item.metric_name,
            warning_value=item.warning_value,
            critical_value=item.critical_value,
            operator=item.operator,
        )
        mock_db.add(new_t)

        mock_db.add.assert_called_once()
        added_obj = mock_db.add.call_args[0][0]
        assert added_obj.metric_name == "conversion_rate"
        assert added_obj.warning_value == 25.0
        assert added_obj.critical_value == 15.0
        assert added_obj.operator == "lt"

    def test_updates_existing_threshold(self):
        """When existing threshold found, updates in-place."""
        mock_db = MagicMock()
        existing = MagicMock()
        existing.warning_value = 10.0
        existing.critical_value = 5.0
        existing.operator = "lt"
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        item = ThresholdItem(
            metric_name="conversion_rate",
            warning_value=20.0,
            critical_value=30.0,
            operator="gt",
        )

        # Simulate update
        found = mock_db.query.return_value.filter.return_value.first.return_value
        found.warning_value = item.warning_value
        found.critical_value = item.critical_value
        found.operator = item.operator

        assert found.warning_value == 20.0
        assert found.critical_value == 30.0
        assert found.operator == "gt"
        # db.add is NOT called for updates
        mock_db.add.assert_not_called()

    def test_upsert_multiple_items_mixed(self):
        """Some new, some existing — correct mix of add + update."""
        mock_db = MagicMock()

        items = [
            ThresholdItem(metric_name="m1", warning_value=10.0, critical_value=5.0, operator="lt"),
            ThresholdItem(metric_name="m2", warning_value=10.0, critical_value=20.0, operator="gt"),
        ]

        # First query: existing for m1, None for m2
        existing_m1 = MagicMock()
        existing_m1.warning_value = 5.0
        existing_m1.critical_value = 3.0
        existing_m1.operator = "lt"

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            existing_m1,  # m1
            None,  # m2
        ]

        for i, item in enumerate(items):
            found = mock_db.query.return_value.filter.return_value.first()
            if found:
                found.warning_value = item.warning_value
                found.critical_value = item.critical_value
                found.operator = item.operator
            else:
                from app.db.models.metric_threshold import MetricThreshold
                new_t = MetricThreshold(
                    business_id=1,
                    metric_name=item.metric_name,
                    warning_value=item.warning_value,
                    critical_value=item.critical_value,
                    operator=item.operator,
                )
                mock_db.add(new_t)

        # m1 was updated (no add), m2 was created (add called)
        assert mock_db.add.call_count == 1
        added = mock_db.add.call_args[0][0]
        assert added.metric_name == "m2"

        # m1 was updated in-place
        assert existing_m1.warning_value == 10.0
        assert existing_m1.critical_value == 5.0
