from __future__ import annotations

import time
from datetime import datetime, timezone


def struct_time_to_utc_datetime(st: time.struct_time) -> datetime:
    return datetime(
        st.tm_year,
        st.tm_mon,
        st.tm_mday,
        st.tm_hour,
        st.tm_min,
        st.tm_sec,
        tzinfo=timezone.utc,
    )
