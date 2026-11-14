"""Download the public NASA OSDR OSD-569 CBC file and verify its SHA-256."""
from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import Request, urlopen

URL = (
    "https://osdr.nasa.gov/geode-py/ws/studies/OSD-569/download"
    "?source=datamanager&file=LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv"
)
EXPECTED_SHA256 = "10a878b009eb2ea11a13fe92ad698098858639e8ed02f5ee849431313b9457d3"
DESTINATION = (
    Path(__file__).resolve().parents[1]
    / "data" / "nasa" / "osd569"
    / "LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv"
)


def main() -> int:
    request = Request(URL, headers={"User-Agent": "ASTRA-Research-Prototype/1.0"})
    with urlopen(request, timeout=45) as response:
        payload = response.read()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != EXPECTED_SHA256:
        raise SystemExit(
            "NASA OSDR file checksum mismatch. "
            f"Expected {EXPECTED_SHA256}, received {actual}. File was not written."
        )
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_bytes(payload)
    print(
        f"Verified NASA OSDR OSD-569 CBC: {len(payload)} bytes, "
        f"SHA-256 {actual}"
    )
    print(f"Saved to {DESTINATION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
