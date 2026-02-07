import json
import glob
import os
from datetime import datetime

# Initialize the search index
search_data = {
    "version": "2.1",
    "generated": datetime.now().strftime("%Y-%m-%d"),
    "stats": {
        "total_modules": 0,
        "total_endpoints": 0,
        "by_category": {}
    },
    "modules": []
}

# Map of model directories to their display names and index page info
model_dirs = {
    "swagger-oper-model": {
        "display": "Operational Data", 
        "type": "operational", 
        "emoji": "🔵",
        "index_page": "swagger-oper-model/index.html"
    },
    "swagger-native-config-model": {
        "display": "Native Config", 
        "type": "config", 
        "emoji": "🟢",
        "index_page": "swagger-native-config-model/index.html"
    },
    "swagger-rpc-model": {
        "display": "RPC Operations", 
        "type": "rpc", 
        "emoji": "🟡",
        "index_page": "swagger-rpc-model/index.html"
    },
    "swagger-events-model": {
        "display": "Events", 
        "type": "events", 
        "emoji": "🟠",
        "index_page": "swagger-events-model/index.html"
    },
    "swagger-cfg-model": {
        "display": "Configuration", 
        "type": "configuration", 
        "emoji": "🔷",
        "index_page": "swagger-cfg-model/index.html"
    },
    "swagger-ietf-model": {
        "display": "IETF Standards", 
        "type": "ietf", 
        "emoji": "🔴",
        "index_page": "swagger-ietf-model/index.html"
    },
    "swagger-openconfig-model": {
        "display": "OpenConfig", 
        "type": "openconfig", 
        "emoji": "🟢",
        "index_page": "swagger-openconfig-model/index.html"
    },
    "swagger-mib-model": {
        "display": "MIB/SNMP", 
        "type": "mib", 
        "emoji": "🟣",
        "index_page": "swagger-mib-model/index.html"
    },
    "swagger-other-model": {
        "display": "Other Models", 
        "type": "other", 
        "emoji": "⚪",
        "index_page": "swagger-other-model/index.html"
    }
}

total_endpoints = 0

# Process each model directory
for model_dir, info in model_dirs.items():
    api_path = os.path.join(model_dir, "api")
    if not os.path.exists(api_path):
        continue
    
    json_files = glob.glob(os.path.join(api_path, "*.json"))
    category_count = 0
    
    for filepath in json_files:
        filename = os.path.basename(filepath)
        
        # Skip manifest and non-spec files
        if 'manifest' in filename.lower() or 'index' in filename.lower():
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                spec = json.load(f)
            
            # Extract module name
            module_name = filename.replace('.json', '')
            module_basename = module_name  # Used for the file name
            
            # Extract paths and create keywords
            keywords = set()
            endpoints = []
            
            # Add the module name variants as keywords
            keywords.add(module_name.lower())
            keywords.add(module_name.lower().replace('cisco-ios-xe-', ''))
            keywords.add(module_name.lower().replace('-', ' '))
            
            # Extract keywords from paths
            if 'paths' in spec:
                for path_url, path_data in spec['paths'].items():
                    total_endpoints += 1
                    
                    # Extract endpoint name from path
                    parts = path_url.split('/')
                    for part in parts:
                        if ':' in part:
                            endpoint_name = part.split(':')[-1]
                            keywords.add(endpoint_name.lower())
                            keywords.add(endpoint_name.lower().replace('-', ' '))
                        elif part and part != 'data' and part != 'operations':
                            keywords.add(part.lower())
                            keywords.add(part.lower().replace('-', ' '))
                    
                    # Extract keywords from operation summaries and descriptions
                    for operation in ['get', 'post', 'put', 'patch', 'delete']:
                        if operation in path_data:
                            if 'summary' in path_data[operation]:
                                summary = path_data[operation]['summary'].lower()
                                words = summary.split()
                                for word in words:
                                    clean_word = word.strip(',.!?;:').lower()
                                    if len(clean_word) >= 3 and clean_word not in ['the', 'and', 'for', 'with', 'from']:
                                        keywords.add(clean_word)
                            
                            if 'description' in path_data[operation]:
                                desc = path_data[operation]['description'].lower()
                                words = desc.split()
                                for word in words:
                                    clean_word = word.strip(',.!?;:').lower()
                                    if len(clean_word) >= 3 and clean_word not in ['the', 'and', 'for', 'with', 'from']:
                                        keywords.add(clean_word)
                    
                    endpoints.append({
                        "path": path_url,
                        "operations": list(path_data.keys())
                    })
            
            # Get description from spec
            description = spec.get('info', {}).get('description', info['display'])
            if description and len(description) > 200:
                description = description[:200] + '...'
            
            # Build the direct Swagger UI URL using hash fragment
            # Format: swagger-native-config-model/index.html#spec=native-00-top-level-leafs
            swagger_url = f"{info['index_page']}#spec={module_basename}"
            
            # Create module entry
            module_entry = {
                "name": module_name,
                "type": info['type'],
                "category": model_dir,
                "displayCategory": info['display'],
                "emoji": info['emoji'],
                "description": description,
                "swaggerUrl": swagger_url,
                "keywords": sorted(list(keywords)),
                "endpoints": len(endpoints),
                "hasTree": os.path.exists(f"yang-trees/{module_name}.html")
            }
            
            # Add YANG tree URL if exists
            if module_entry["hasTree"]:
                module_entry["yangTreeUrl"] = f"yang-trees/{module_name}.html"
            
            search_data["modules"].append(module_entry)
            category_count += 1
            
        except Exception as e:
            print(f"⚠️  Error processing {filename}: {e}")
            continue
    
    if category_count > 0:
        search_data["stats"]["by_category"][model_dir] = category_count

# Update totals
search_data["stats"]["total_modules"] = len(search_data["modules"])
search_data["stats"]["total_endpoints"] = total_endpoints

# Write the search index
with open('search-index.json', 'w', encoding='utf-8') as f:
    json.dump(search_data, f, indent=2)

print(f"\n✅ Generated search index with direct spec links:")
print(f"   - {search_data['stats']['total_modules']} modules")
print(f"   - {total_endpoints} total endpoints")
print(f"   - Categories: {len(search_data['stats']['by_category'])}")
print(f"\n📝 Sample URL from first module:")
if search_data["modules"]:
    first_module = search_data["modules"][0]
    print(f"   Module: {first_module['name']}")
    print(f"   URL: {first_module['swaggerUrl']}")
    print(f"   Keywords: {len(first_module['keywords'])} total")
