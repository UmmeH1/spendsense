import pandas as pd
import re

# Step A: Load the raw file exactly as the bank gave it to us
df = pd.read_csv("/mnt/user-data/uploads/Checking.csv")

# Step B: Turn the DATE column (currently just text) into a real date
# This lets us sort by date, group by month, etc. later on
df["DATE"] = pd.to_datetime(df["DATE"], format="%m/%d/%Y")

# Step C: Split into spending (negative amounts) vs income (positive amounts)
# Spending is what we actually want to analyze for "unusual" purchases
df["type"] = df["AMOUNT"].apply(lambda x: "spending" if x < 0 else "income")

# Make spending amounts positive numbers (easier to read/chart -
# a $50 purchase should just say 50, not -50)
df["amount_clean"] = df["AMOUNT"].abs()

# Step D: Simplify the messy description into a short, readable merchant name
def simplify_description(desc):
    desc = desc.strip()
    # Zelle transfers - keep it simple
    if "ZELLE FROM" in desc:
        return "Zelle (received)"
    if "ZELLE TO" in desc:
        return "Zelle (sent)"
    # Payroll deposits
    if "PAYROLL" in desc:
        return "Paycheck"
    # Card purchases - pull out just the merchant name
    if "PURCHASE" in desc and "AUTHORIZED ON" in desc:
        match = re.search(r"AUTHORIZED ON\s+\d{2}/\d{2}\s+(.+?)\s{2,}", desc)
        if match:
            return match.group(1).strip()
    # Credit card / loan payments
    if "CHASE CREDIT" in desc:
        return "Chase Credit Card Payment"
    if "DISCOVER" in desc:
        return "Discover Payment"
    # Fallback: just return the first few words
    return " ".join(desc.split()[:3])

df["merchant"] = df["DESCRIPTION"].apply(simplify_description)

# Step E: Assign a simple category based on keywords in the merchant name
def categorize(merchant, desc):
    text = (merchant + " " + desc).upper()
    if "PAYCHECK" in merchant.upper() or "PAYROLL" in desc.upper():
        return "income"
    if "ZELLE" in merchant.upper() or "ONLINE TRANSFER" in text or "MONEY TRANSFER" in text:
        return "transfer"
    if any(k in text for k in [
        "DOORDASH", "UBER EATS", "GRUBHUB", "PIZZA", "CHILIS", "RESTAURANT",
        "IN-N-OUT", "MCDONALD", "CHICK-FIL-A", "DOMINO'S", "LA MADELEINE",
        "FIRST WATCH", "PIADA", "TST*", "SWIG", "COFFEE", "CAFE", "THAI",
        "CHICKEN", "ITALIAN", "NOODLE"
    ]):
        return "dining"
    if any(k in text for k in ["KROGER", "MITSUWA", "MARKETPLAC"]):
        return "groceries"
    if any(k in text for k in ["CRUNCH", "FIT CLUB"]):
        return "fitness"
    if any(k in text for k in ["TARGET", "WALMART", "AMAZON", "MKTPL", "TIKTOK SHOP", "SEPHORA", "LUSH", "KINDLE"]):
        return "shopping"
    if any(k in text for k in ["MURPHY EXPRESS", "MURPHY USA", "SHELL", "EXXON", "CHEVRON", "RACETRAC", "QUIKTRIP", "7-ELEVEN"]):
        return "gas"
    if any(k in text for k in ["UBER", "NTTA"]):
        return "transportation"
    if any(k in text for k in ["CHASE CREDIT", "DISCOVER", "CREDIT CRD"]):
        return "credit card payment"
    if any(k in text for k in ["STATE FARM", "INSURA"]):
        return "insurance"
    if any(k in text for k in ["NAIL", "SPA", "SALON"]):
        return "personal care"
    if any(k in text for k in ["PARCHMENT", "CSC SERVICEWO", "AIR/TIRE"]):
        return "services"
    return "other"

df["category"] = df.apply(lambda row: categorize(row["merchant"], row["DESCRIPTION"]), axis=1)

# Step F: Save the cleaned version
output_cols = ["DATE", "merchant", "category", "type", "amount_clean"]
clean_df = df[output_cols].rename(columns={
    "DATE": "date",
    "amount_clean": "amount"
})

clean_df.to_csv("/home/claude/cleaned_transactions.csv", index=False)

print("Done! Here's a preview of the cleaned data:\n")
print(clean_df.head(15).to_string(index=False))
print(f"\nTotal rows: {len(clean_df)}")
print(f"\nCategory breakdown:")
print(clean_df["category"].value_counts())
