import kagglehub

print("Downloading Kaggle malicious URLs dataset...")
print("Dataset: sid321axn/malicious-urls-dataset")
print("-" * 60)

try:
    path = kagglehub.dataset_download("sid321axn/malicious-urls-dataset")
    print("\n✅ Download complete!")
    print(f"Path to dataset files: {path}")
    
    import os
    print("\nFiles in dataset:")
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        size = os.path.getsize(file_path) / 1024
        print(f"  - {file} ({size:.2f} KB)")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nNote: You may need to authenticate with Kaggle first.")
    print("Run: kaggle config set -n username -v YOUR_USERNAME")
