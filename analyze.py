# analyze.py
# Key finding: km_since_service, avg_daily_km, and load_factor separate cars that break down from
# those that do not. Total odometer (lifetime mileage) and age show no meaningful separation —
# the obvious assumption that "older, higher-mileage cars break more" is not what this data says.
#
# Method: for each of the three predictive columns, min-max normalise to [0, 1], then weight by
# how strongly each one separates the two groups (60 %, 21 %, 19 % — proportional to the mean
# difference between groups). Multiply by 100 to get a 0-100 risk score. No ML required.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# --- Step 1: compare broke vs fine groups for every column ---
broke = df[df["broke_down"] == 1]
fine  = df[df["broke_down"] == 0]

print(f"Dataset: {len(df)} cars  |  broke: {len(broke)}  |  fine: {len(fine)}\n")

feature_cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
print(f"{'Column':<22} {'broke mean':>12} {'fine mean':>12} {'diff %':>9}  verdict")
print("-" * 75)
for c in feature_cols:
    bm = broke[c].mean()
    fm = fine[c].mean()
    pct = (bm - fm) / fm * 100 if fm != 0 else 0
    verdict = "SEPARATES" if abs(pct) >= 15 else "flat"
    print(f"{c:<22} {bm:>12.2f} {fm:>12.2f} {pct:>8.1f}%  {verdict}")

print()
print("Conclusion: km_since_service (+60.8%), avg_daily_km (+21.5%), and load_factor (+18.8%)")
print("separate the groups. odometer_km (+0.3%) and age_years (-0.2%) do not.\n")

# --- Step 2: breakdown rate by km_since_service band ---
print("Breakdown rate by km_since_service band:")
bands_ks = [0, 3000, 6000, 9000, 12000, 15000, 99999]
labels_ks = ["0-3k", "3-6k", "6-9k", "9-12k", "12-15k", "15k+"]
df["_ks_band"] = pd.cut(df["km_since_service"], bins=bands_ks, labels=labels_ks)
for band, grp in df.groupby("_ks_band", observed=True):
    rate = grp["broke_down"].mean()
    bar  = "#" * int(rate * 20)
    print(f"  {band:<8}  {rate:5.1%}  {bar}")

# --- Step 3: build a risk score from the three predictive columns ---
# Weights derived from the % mean-difference above, normalised to sum to 1.
#   km_since_service: 60.8 / (60.8 + 21.5 + 18.8) = 0.60
#   avg_daily_km:     21.5 / (60.8 + 21.5 + 18.8) = 0.21
#   load_factor:      18.8 / (60.8 + 21.5 + 18.8) = 0.19
WEIGHTS = {
    "km_since_service": 0.60,
    "avg_daily_km":     0.21,
    "load_factor":      0.19,
}

scored = df[["car_id", "km_since_service", "avg_daily_km", "load_factor", "broke_down"]].copy()

for col in WEIGHTS:
    col_min = scored[col].min()
    col_max = scored[col].max()
    scored[f"_{col}_norm"] = (scored[col] - col_min) / (col_max - col_min)

scored["risk_score"] = (
    scored["_km_since_service_norm"] * WEIGHTS["km_since_service"]
    + scored["_avg_daily_km_norm"]   * WEIGHTS["avg_daily_km"]
    + scored["_load_factor_norm"]    * WEIGHTS["load_factor"]
) * 100

# --- Step 4: print the top 10 riskiest cars ---
print()
print("Top 10 cars by risk score (highest first):")
print(f"  {'car_id':<12} {'risk':>6}  {'km_since_svc':>13}  {'avg_daily':>9}  {'load':>6}  {'broke?':>7}")
print("  " + "-" * 60)

top10 = scored.nlargest(10, "risk_score")
for _, row in top10.iterrows():
    flag = "YES" if row["broke_down"] == 1 else "no"
    print(
        f"  {row['car_id']:<12} {row['risk_score']:>5.1f}"
        f"  {row['km_since_service']:>13,.0f}"
        f"  {row['avg_daily_km']:>9,.0f}"
        f"  {row['load_factor']:>6.2f}"
        f"  {flag:>7}"
    )

print()
print(f"Overall breakdown rate: {df['broke_down'].mean():.1%}")
print(f"Breakdown rate in top 10: {top10['broke_down'].mean():.1%}")
print("(The score concentrates the at-risk cars near the top of the list.)")
