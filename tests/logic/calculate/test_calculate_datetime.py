from datetime import datetime
from zoneinfo import ZoneInfo

from freezegun import freeze_time

from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now, get_now_UTC


# 使用ライブラリ:freezegun
# テスト中の時間を「2025年10月1日12時（UTC）」に固定
# タイムゾーンが Asia/Tokyo なので、UTC+9時間（日本時間）となり、結果「2025-10-01 21:00:00+09:00」が result になる。
@freeze_time("2025-10-01 12:00:00+00:00")
def test_get_now() -> None:
    result = get_now()
    expected = datetime(
        year=2025, month=10, day=1, hour=21, minute=0, second=0, tzinfo=ZoneInfo("Asia/Tokyo")
    )

    # 検証
    assert result == expected
    assert result.tzinfo == ZoneInfo("Asia/Tokyo")


@freeze_time("2025-10-01 12:00:00+00:00")
def test_get_now_utc() -> None:
    result = get_now_UTC()
    expected = datetime(year=2025, month=10, day=1, hour=12, minute=0, second=0)

    # 検証
    assert result == expected
