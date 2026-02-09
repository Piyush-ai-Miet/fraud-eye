import pandas as pd
import os
import shutil

# Auto-detect Kaggle dataset path
try:
    import kagglehub
    dataset_path = kagglehub.dataset_download("sid321axn/malicious-urls-dataset")
    dataset_path = f"{dataset_path}/malicious_phish.csv"
except:
    # Fallback to manual path
    dataset_path = "data/kaggle_malicious_urls.csv"

print("="*60)
print("PROCESSING KAGGLE MALICIOUS URLs DATASET")
print("="*60)

df = pd.read_csv(dataset_path)

print(f"\nDataset Shape: {df.shape}")
print(f"Total URLs: {len(df)}")
print(f"\nColumns: {list(df.columns)}")

print("\n" + "-"*60)
print("LABEL DISTRIBUTION")
print("-"*60)
print(df['type'].value_counts())

print("\n" + "-"*60)
print("SAMPLE URLs")
print("-"*60)
for label in df['type'].unique()[:5]:
    print(f"\n{label.upper()}:")
    samples = df[df['type'] == label]['url'].head(3)
    for url in samples:
        print(f"  - {url}")

# Copy to data folder
output_path = "data/kaggle_malicious_urls.csv"
shutil.copy(dataset_path, output_path)
print(f"\n✅ Dataset copied to: {output_path}")

# Create a smaller training set (balanced)
print("\n" + "="*60)
print("CREATING BALANCED TRAINING SET")
print("="*60)

# Sample 1000 URLs from each category
sample_size = 1000
balanced_df = pd.DataFrame()

for label in df['type'].unique():
    label_df = df[df['type'] == label]
    sample = label_df.sample(n=min(sample_size, len(label_df)), random_state=42)
    balanced_df = pd.concat([balanced_df, sample])

balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nBalanced Dataset Shape: {balanced_df.shape}")
print(f"Total URLs: {len(balanced_df)}")
print("\nLabel Distribution:")
print(balanced_df['type'].value_counts())

# Save balanced dataset
balanced_path = "data/kaggle_balanced_urls.csv"
balanced_df.to_csv(balanced_path, index=False)
print(f"\n✅ Balanced dataset saved to: {balanced_path}")

print("\n" + "="*60)
print("DATASET PROCESSING COMPLETE")
print("="*60)
