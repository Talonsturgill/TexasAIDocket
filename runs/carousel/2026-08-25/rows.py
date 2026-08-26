"""Frame 2 and frame 3's rows, COMPOSED from figures.json rather than typed onto the slide."""
import json, collections, pathlib
f=json.load(open("out/2026-08-25/figures.json"))
marks=f["chronology"]["marks"]
MON="January February March April May June July August September October November December".split()
by_month=collections.Counter()
for m in marks: by_month[int(m["date"][5:7])]+=1
print("FRAME 3, months:")
for mo in sorted(by_month):
    print(f"   {MON[mo-1].upper():<10} {by_month[mo]}")
print("   total", sum(by_month.values()))
print("\nFRAME 2, fourteen rows in chronology order:")
for i,m in enumerate(marks):
    print(f'   {i+1:>2}  {m["shape"]:<22} {m["place"]:<18} {m["claim"]}')
print("\nplaces:", sorted({m["place"] for m in marks}))
counts=collections.Counter(m["place"] for m in marks)
print("repeat:", {k:v for k,v in counts.items() if v>1})
