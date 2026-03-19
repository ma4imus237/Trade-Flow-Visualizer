import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.shift_detector import ShiftDetector


@pytest.mark.asyncio
async def test_detect_shifts_finds_surge(seeded_session: AsyncSession):
    """AUS->CHN: 5M in 2020, 15M in 2023 => 200% increase => surge."""
    detector = ShiftDetector(seeded_session)
    shifts = await detector.detect_shifts("lithium", 2020, 2023, min_value=1_000_000)
    surge_shifts = [s for s in shifts if s.shift_type == "surge"]
    aus_chn = [
        s for s in surge_shifts
        if s.reporter_iso3 == "AUS" and s.partner_iso3 == "CHN"
    ]
    assert len(aus_chn) == 1
    assert aus_chn[0].change_pct == 200.0


@pytest.mark.asyncio
async def test_detect_shifts_finds_collapse(seeded_session: AsyncSession):
    """AUS->USA: 3M in 2020, 1M in 2023 => -66.7% decrease => collapse."""
    detector = ShiftDetector(seeded_session)
    shifts = await detector.detect_shifts("lithium", 2020, 2023, min_value=1_000_000)
    collapse_shifts = [s for s in shifts if s.shift_type == "collapse"]
    aus_usa = [
        s for s in collapse_shifts
        if s.reporter_iso3 == "AUS" and s.partner_iso3 == "USA"
    ]
    assert len(aus_usa) == 1
    assert aus_usa[0].change_pct < -50.0


@pytest.mark.asyncio
async def test_detect_shifts_finds_new(seeded_session: AsyncSession):
    """BRA->CHN: 0 in 2020, 8M in 2023 => new flow."""
    detector = ShiftDetector(seeded_session)
    shifts = await detector.detect_shifts("lithium", 2020, 2023, min_value=1_000_000)
    new_shifts = [s for s in shifts if s.shift_type == "new"]
    bra_chn = [
        s for s in new_shifts
        if s.reporter_iso3 == "BRA" and s.partner_iso3 == "CHN"
    ]
    assert len(bra_chn) == 1
    assert bra_chn[0].value_from == 0
    assert bra_chn[0].value_to == 8_000_000


@pytest.mark.asyncio
async def test_detect_shifts_finds_abandoned(seeded_session: AsyncSession):
    """CHN->USA: 2M in 2020, 0 in 2023 => abandoned."""
    detector = ShiftDetector(seeded_session)
    shifts = await detector.detect_shifts("lithium", 2020, 2023, min_value=1_000_000)
    abandoned_shifts = [s for s in shifts if s.shift_type == "abandoned"]
    chn_usa = [
        s for s in abandoned_shifts
        if s.reporter_iso3 == "CHN" and s.partner_iso3 == "USA"
    ]
    assert len(chn_usa) == 1
    assert chn_usa[0].value_to == 0


@pytest.mark.asyncio
async def test_detect_shifts_sorted_by_abs_change(seeded_session: AsyncSession):
    detector = ShiftDetector(seeded_session)
    shifts = await detector.detect_shifts("lithium", 2020, 2023)
    abs_changes = [abs(s.change_abs) for s in shifts]
    assert abs_changes == sorted(abs_changes, reverse=True)


@pytest.mark.asyncio
async def test_summary_shifts(seeded_session: AsyncSession):
    detector = ShiftDetector(seeded_session)
    summary = await detector.summary_shifts("lithium", 2020, 2023)
    assert summary.commodity == "lithium"
    assert summary.total_shifts > 0
    total = summary.surges + summary.collapses + summary.new_flows + summary.abandoned_flows
    assert total == summary.total_shifts
    assert len(summary.top_shifts) <= 20


@pytest.mark.asyncio
async def test_summary_shifts_has_all_types(seeded_session: AsyncSession):
    detector = ShiftDetector(seeded_session)
    summary = await detector.summary_shifts("lithium", 2020, 2023)
    assert summary.surges >= 1
    assert summary.collapses >= 1
    assert summary.new_flows >= 1
    assert summary.abandoned_flows >= 1
