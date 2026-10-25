
from datetime import datetime

dates = ["300960", "010120", "230367"]

print("Testing Date Parsing:")
for d in dates:
    dt = datetime.strptime(d, "%d%m%y")
    print(f"{d} -> {dt.strftime('%Y-%m-%d')}")
