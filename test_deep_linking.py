import json

# Test the search index and deep linking URLs

print("=" * 70)
print("DEEP LINKING NAVIGATION TEST")
print("=" * 70)

# Load the search index
with open('search-index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n✅ Search Index Version: {data['version']}")
print(f"✅ Total Modules: {data['stats']['total_modules']}")
print(f"✅ Total Endpoints: {data['stats']['total_endpoints']}")

# Test 1: Find modules with "hostname" keyword
print("\n" + "=" * 70)
print("TEST 1: Search for 'hostname'")
print("=" * 70)

hostname_modules = [m for m in data['modules'] if 'hostname' in m['keywords']]
print(f"\nFound {len(hostname_modules)} module(s) with 'hostname' keyword:")

for module in hostname_modules:
    print(f"\n  Module: {module['name']}")
    print(f"  Category: {module['displayCategory']} {module['emoji']}")
    print(f"  Deep Link URL: {module['swaggerUrl']}")
    print(f"  Keywords: {len(module['keywords'])} total")
    print(f"  Endpoints: {module['endpoints']}")
    
    # Verify URL format
    if '#spec=' in module['swaggerUrl']:
        print(f"  ✅ URL uses hash fragment (deep linking enabled)")
    else:
        print(f"  ❌ URL missing hash fragment!")

# Test 2: Find modules with "interface" keyword
print("\n" + "=" * 70)
print("TEST 2: Search for 'interface'")
print("=" * 70)

interface_modules = [m for m in data['modules'] if 'interface' in m['keywords']]
print(f"\nFound {len(interface_modules)} module(s) with 'interface' keyword")
print(f"\nSample modules:")

for module in interface_modules[:5]:  # Show first 5
    print(f"\n  • {module['name']}")
    print(f"    URL: {module['swaggerUrl']}")

# Test 3: Verify all URLs have hash fragments
print("\n" + "=" * 70)
print("TEST 3: Verify all URLs use hash-based deep linking")
print("=" * 70)

correct_urls = 0
incorrect_urls = 0

for module in data['modules']:
    if '#spec=' in module['swaggerUrl']:
        correct_urls += 1
    else:
        incorrect_urls += 1
        print(f"  ❌ Missing hash: {module['swaggerUrl']}")

print(f"\n✅ Correct URLs (with #spec=): {correct_urls}")
print(f"❌ Incorrect URLs: {incorrect_urls}")

if incorrect_urls == 0:
    print(f"\n🎉 SUCCESS! All {correct_urls} modules have deep linking enabled!")
else:
    print(f"\n⚠️  WARNING: {incorrect_urls} modules missing deep linking!")

# Test 4: Verify URL format consistency
print("\n" + "=" * 70)
print("TEST 4: URL Format Examples by Category")
print("=" * 70)

categories = {}
for module in data['modules']:
    cat = module['category']
    if cat not in categories:
        categories[cat] = module

print("\nExpected URL format: <category>/index.html#spec=<module-name>\n")

for cat, module in sorted(categories.items()):
    expected_prefix = f"{cat}/index.html#spec="
    if module['swaggerUrl'].startswith(expected_prefix):
        print(f"✅ {cat}")
        print(f"   Sample: {module['swaggerUrl']}")
    else:
        print(f"❌ {cat}")
        print(f"   Got: {module['swaggerUrl']}")
        print(f"   Expected prefix: {expected_prefix}")

print("\n" + "=" * 70)
print("DEEP LINKING TEST COMPLETE")
print("=" * 70)
print(f"\nNext step: Open index.html in browser and test actual navigation")
print(f"Try searching for: hostname, interface, bgp, ospf, vlan")
print(f"Click a search result and verify Swagger UI loads immediately")
