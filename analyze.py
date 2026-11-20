import csv
import sys
from collections import Counter
from datetime import datetime


def to_sec(ts):
    t = datetime.strptime(ts, "%H:%M:%S.%f")
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6


def summarize(name, rows):
    zones = Counter(r["zone"] for r in rows if not r["error"])
    errors = sum(1 for r in rows if r["error"])
    ok = sum(zones.values())
    print(f"\n[{name}] requests={len(rows)} errors={errors}")
    for zone, n in sorted(zones.items()):
        print(f"  {zone}: {n} ({n / ok * 100:.1f}%)")


client_csv, events_csv, killed_zone = sys.argv[1], sys.argv[2], sys.argv[3]

with open(events_csv) as f:
    events = {r["event"]: to_sec(r["timestamp"]) for r in csv.DictReader(f)}
kill_t, restart_t = events["kill"], events["restart"]

with open(client_csv) as f:
    rows = list(csv.DictReader(f))
for r in rows:
    r["t"] = to_sec(r["timestamp"])

baseline = [r for r in rows if r["t"] < kill_t]
down = [r for r in rows if kill_t <= r["t"] < restart_t]
recovered = [r for r in rows if r["t"] >= restart_t]

# 故障发现：kill 之后最后一个错误
down_errors = [r["t"] for r in down if r["error"]]
if down_errors:
    print(f"Failover detection: {max(down_errors) - kill_t:.1f}s "
          f"({len(down_errors)} failed requests)")
else:
    print("Failover detection: no errors observed in this run")

# 恢复：restart 之后第一次重新出现被 kill 的 zone
back = [r["t"] for r in recovered if r["zone"] == killed_zone]
recovery_t = min(back) if back else None
if recovery_t:
    print(f"Recovery detection: {recovery_t - restart_t:.1f}s")
else:
    print("Recovery detection: killed zone never came back")

summarize("A. baseline (both healthy)", baseline)
summarize("B. one server down", down)
summarize("C. after restart (all)", recovered)
if recovery_t:
    summarize("C'. after recovery (both healthy again)",
              [r for r in recovered if r["t"] >= recovery_t])