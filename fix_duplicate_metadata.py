import os
import re
from pathlib import Path

# Directory containing YANG tree HTML files
trees_dir = "yang-trees"

# Counter for files processed
files_fixed = 0
total_duplicates_removed = 0

# Get all HTML files in yang-trees directory
html_files = list(Path(trees_dir).glob("*.html"))

print(f"Found {len(html_files)} HTML files to process...")

for file_path in html_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to match the duplicate metadata section
        metadata_pattern = r'<div style="background: #fff9e6; border-left: 4px solid #FFA726;[^>]+>.*?<p style="color: #E65100[^>]+><strong>📋 Module Metadata</strong></p>.*?</div>'
        
        # Pattern to match the duplicate example usage section
        example_pattern = r'<div style="background: #e8f5e9; border-left: 4px solid #4CAF50;[^>]+>.*?<p style="color: #2E7D32[^>]+><strong>💡 Example Usage</strong></p>.*?</div>'
        
        # Find all metadata sections
        metadata_matches = list(re.finditer(metadata_pattern, content, re.DOTALL))
        example_matches = list(re.finditer(example_pattern, content, re.DOTALL))
        
        duplicates_in_file = 0
        
        # If there are multiple metadata sections, remove all but the first
        if len(metadata_matches) > 1:
            print(f"\n{file_path.name}: Found {len(metadata_matches)} metadata sections")
            # Keep the first one, remove the rest
            for match in reversed(metadata_matches[1:]):  # Reverse to maintain indices
                content = content[:match.start()] + content[match.end():]
                duplicates_in_file += 1
        
        # If there are multiple example sections, remove all but the first
        if len(example_matches) > 1:
            print(f"{file_path.name}: Found {len(example_matches)} example sections")
            # Re-find matches after metadata removal
            example_matches = list(re.finditer(example_pattern, content, re.DOTALL))
            # Keep the first one, remove the rest
            for match in reversed(example_matches[1:]):  # Reverse to maintain indices
                content = content[:match.start()] + content[match.end():]
                duplicates_in_file += 1
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            files_fixed += 1
            total_duplicates_removed += duplicates_in_file
            print(f"  ✅ Fixed {duplicates_in_file} duplicate sections")
    
    except Exception as e:
        print(f"  ❌ Error processing {file_path.name}: {e}")

print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"Total files processed: {len(html_files)}")
print(f"Files fixed: {files_fixed}")
print(f"Total duplicate sections removed: {total_duplicates_removed}")
print(f"✅ All duplicates removed!")
