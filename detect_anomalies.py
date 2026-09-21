import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("/home/claude/cleaned_transactions.csv")

# We only care about SPENDING for anomaly detection, not income/transfers
spending = df[df["type"] == "spending"].copy()

# Only run detection on categories with enough transactions to learn a pattern from.
# With very few points (like 1-2), the model has nothing to compare against.
MIN_TRANSACTIONS = 5

spending["anomaly"] = "normal"  # default everyone to normal first

for category in spending["category"].unique():
    cat_data = spending[spending["category"] == category]

    if len(cat_data) < MIN_TRANSACTIONS:
        continue  # skip categories with too few transactions to judge

    # Isolation Forest expects a 2D table of numbers, so we reshape the amounts
    amounts = cat_data[["amount"]]

    # contamination=0.1 roughly means "expect about 10% of this category
    # to be flagged as unusual" -- a reasonable starting guess
    model = IsolationForest(contamination=0.1, random_state=42)
    predictions = model.fit_predict(amounts)
    # IsolationForest returns -1 for anomalies, 1 for normal points

    spending.loc[cat_data.index, "anomaly"] = [
        "flagged" if p == -1 else "normal" for p in predictions
    ]

# Save the result
spending.to_csv("/home/claude/spending_with_anomalies.csv", index=False)

# Show the flagged transactions so we can sanity-check them
flagged = spending[spending["anomaly"] == "flagged"].sort_values("amount", ascending=False)
print(f"Total spending transactions analyzed: {len(spending)}")
print(f"Flagged as unusual: {len(flagged)}\n")
print(flagged[["date", "merchant", "category", "amount"]].to_string(index=False))
