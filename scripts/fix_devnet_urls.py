#!/usr/bin/env python3
"""Replace old developer.cisco.com/iosxe URLs with developer.cisco.com/iosxe"""
import os
import sys


def main():

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OLD = 'developer.cisco.com/iosxe'
    NEW = 'developer.cisco.com/iosxe'

    total_files = 0
    total_occurrences = 0

    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Skip .git
        if '.git' in dirpath:
            continue
        for filename in filenames:
            if not filename.endswith(('.json', '.html', '.py', '.md')):
                continue
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            if OLD not in content:
                continue
            count = content.count(OLD)
            total_occurrences += count
            total_files += 1
            new_content = content.replace(OLD, NEW)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            rel = os.path.relpath(filepath, ROOT)
            print(f"  {rel} ({count} replacements)")

    print(f"\nDone: {total_files} files updated, {total_occurrences} total replacements")

if __name__ == '__main__':
    main()
