#!/usr/bin/env python3
"""
Load Kaggle URLs into malicious_urls.csv database
"""

import pandas as pd
import csv

print("\n" + "="*60)
print("📊 LOADING KAGGLE URLS TO DATABASE")
print("="*60 + "\n")

# Load Kaggle dataset
kaggle_df = pd.read_csv('data/kaggle_balanced_urls.csv')

print(f"Kaggle dataset: {len(kaggle_df)} URLs")
print(f"Distribution:")
print(kaggle_df['type'].value_counts())
print()

# Load existing malicious_urls.csv
try:
    existing_df = pd.read_csv('data/malicious_urls.csv')
    print(f"Existing database: {len(existing_df)} URLs")
except:
    existing_df = pd.DataFrame(columns=['url', 'label', 'category'])
    print("Creating new database...")

# Convert Kaggle format to our format
new_urls = []
for _, row in kaggle_df.iterrows():
    url = row['url']
    url_type = row['type']
    
    # Map Kaggle types to our categories
    if url_type == 'benign':
        label = 'benign'
        category = 'safe'
    elif url_type == 'phishing':
        label = 'malicious'
        category = 'phishing'
    elif url_type == 'malware':
        label = 'malicious'
        category = 'malware'
    elif url_type == 'defacement':
        label = 'malicious'
        category = 'defacement'
    else:
        label = 'malicious'
        category = 'suspicious'
    
    new_urls.append({
        'url': url,
        'label': label,
        'category': category
    })

new_df = pd.DataFrame(new_urls)

# Combine with existing (remove duplicates)
combined_df = pd.concat([existing_df, new_df], ignore_index=True)
combined_df = combined_df.drop_duplicates(subset=['url'], keep='first')

print(f"\nCombined database: {len(combined_df)} URLs")
print(f"Malicious: {len(combined_df[combined_df['label'] == 'malicious'])}")
print(f"Benign: {len(combined_df[combined_df['label'] == 'benign'])}")

# Save to CSV
combined_df.to_csv('data/malicious_urls.csv', index=False)

print(f"\n✅ Database updated: data/malicious_urls.csv")
print(f"Total URLs: {len(combined_df)}")

# Show sample malicious URLs
print(f"\n📋 Sample Malicious URLs:")
malicious_sample = combined_df[combined_df['label'] == 'malicious'].head(10)
for i, row in malicious_sample.iterrows():
    print(f"  {row['category']:12} : {row['url'][:60]}")

print("\n" + "="*60)
print("✅ Kaggle URLs loaded into database!")
print("="*60 + "\n")
