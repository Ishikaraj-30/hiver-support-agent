import pandas as pd

print("Loading amazon_threads.csv...")
df = pd.read_csv("amazon_threads.csv", low_memory=False)

# Split into customer tweets and brand replies
inbound = df[df["inbound"] == True].copy()
outbound = df[df["inbound"] == False].copy()

# Ensure ID columns are treated as strings
inbound["tweet_id"] = inbound["tweet_id"].astype(str)
outbound["in_response_to_tweet_id"] = (
    outbound["in_response_to_tweet_id"].astype(str).str.split(".").str[0]
)

# Merge: match inbound tweet to the response tweet
merged = outbound.merge(
    inbound,
    left_on="in_response_to_tweet_id",
    right_on="tweet_id",
    suffixes=("_brand", "_customer"),
)

print(f"Total matched pairs found: {len(merged)}")

paired_df = pd.DataFrame(
    {
        "thread_id": merged["tweet_id_customer"],
        "customer_text": merged["text_customer"],
        "brand_text": merged["text_brand"],
    }
).drop_duplicates(subset=["customer_text"])

output_file = "reconstructed_pairs.csv"
paired_df.to_csv(output_file, index=False, encoding="utf-8")
print(f"Successfully saved {len(paired_df)} unique pairs to {output_file}!")