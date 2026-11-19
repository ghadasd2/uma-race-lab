"""CN team (and my teams) vs random mock teams. Usage: loh_v3_calibrate.py N"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from umasim import loh, mock
n = int(sys.argv[1])
teams = {"base": loh.opponent_team("cn"),
         "my_v2_stats": json.loads(Path("data/loh/my_team_v2_stats.json").read_text())}
t = time.time()
df = mock.evaluate(teams, list(range(40_000_000, 40_000_000 + n)))
s = mock.summarize(df)
print(s.round(2).to_string()); print(f"{len(df)} races in {time.time() - t:.0f}s")
