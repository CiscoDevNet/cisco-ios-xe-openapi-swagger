#!/usr/bin/env python3
"""
Corrected audit: Find YANG modules with REAL dual roles.
Only counts containers/lists/leaves that are top-level data nodes,
not those nested inside rpc/notification/grouping blocks.
"""
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
yang_dir = os.path.join(BASE, "references", "17181-YANG-modules")


def strip_comments(content):
    """Remove YANG block and line comments."""
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    return content


def find_block_end(content, start):
    depth = 0
    i = start
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(content) - 1

def has_real_data_nodes(yang_content):
    """Check if module has real top-level container/list/leaf data nodes
    (not inside rpc, notification, grouping, augment, typedef, identity)."""
    content = strip_comments(yang_content)
    
    # Support both module and submodule declarations
    module_match = re.search(r'(?:sub)?module\s+\S+\s*\{', content)
    if not module_match:
        return False, []
    
    nodes = []
    depth = 1
    i = module_match.end()
    data_node_types = ('container', 'list', 'leaf-list', 'leaf')
    skip_blocks = {'grouping', 'rpc', 'notification', 'augment', 'typedef', 'identity', 'extension', 'feature', 'deviation'}
    
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                break
        
        if depth == 1:
            matched = False
            # Check for data nodes at top level (order matters: leaf-list before leaf)
            for node_type in data_node_types:
                m = re.match(rf'{node_type}\s+(\S+)\s*\{{', content[i:])
                if m:
                    nodes.append(f"{node_type} {m.group(1)}")
                    brace_pos = i + m.end() - 1
                    i = find_block_end(content, brace_pos) + 1
                    matched = True
                    break
            
            # Skip blocks we don't care about
            if not matched:
                for skip_type in skip_blocks:
                    m = re.match(rf'{skip_type}\s+', content[i:])
                    if m:
                        brace_match = re.search(r'\{', content[i:])
                        if brace_match:
                            brace_pos = i + brace_match.start()
                            i = find_block_end(content, brace_pos) + 1
                            matched = True
                            break
            
            if matched:
                continue
        
        i += 1
    
    return len(nodes) > 0, nodes

def _find_top_level_statements(yang_content, stmt_type):
    """Find top-level statements of a given type using brace-depth parsing."""
    content = strip_comments(yang_content)
    module_match = re.search(r'(?:sub)?module\s+\S+\s*\{', content)
    if not module_match:
        return []
    
    names = []
    depth = 1
    i = module_match.end()
    
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                break
        
        if depth == 1:
            m = re.match(rf'{stmt_type}\s+(\S+)\s*\{{', content[i:])
            if m:
                names.append(m.group(1))
                brace_pos = i + m.end() - 1
                i = find_block_end(content, brace_pos) + 1
                continue
        
        i += 1
    
    return names


def has_notifications(yang_content):
    """Check if module has top-level notification statements."""
    notifs = _find_top_level_statements(yang_content, 'notification')
    return len(notifs) > 0, notifs


def has_rpcs(yang_content):
    """Check if module has top-level rpc statements."""
    rpcs = _find_top_level_statements(yang_content, 'rpc')
    return len(rpcs) > 0, rpcs

# Check spec locations
model_folders = {
    'oper': 'swagger-oper-model',
    'cfg': 'swagger-cfg-model',
    'native': 'swagger-native-config-model',
    'openconfig': 'swagger-openconfig-model',
    'ietf': 'swagger-ietf-model',
    'mib': 'swagger-mib-model',
    'rpc': 'swagger-rpc-model',
    'events': 'swagger-events-model',
    'other': 'swagger-other-model',
}

def main():
    if not os.path.isdir(yang_dir):
        print(f"ERROR: YANG directory not found: {yang_dir}", file=sys.stderr)
        sys.exit(1)

    all_spec_modules = {}
    for label, folder in model_folders.items():
        for api in ['api', 'api']:
            p = os.path.join(BASE, folder, api)
            if os.path.isdir(p):
                for fn in os.listdir(p):
                    if fn.endswith('.json') and fn != 'manifest.json':
                        name = fn.replace('.json', '')
                        all_spec_modules.setdefault(name, set()).add(label)

    # Analyze all YANG modules
    dual_modules = []
    for fn in sorted(os.listdir(yang_dir)):
        if not fn.endswith('.yang'):
            continue
        name = re.sub(r'@\d{4}-\d{2}-\d{2}$', '', fn.replace('.yang', ''))
        with open(os.path.join(yang_dir, fn), encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        has_augment_native = bool(re.search(r'augment\s+"/ios:', content))
        if has_augment_native:
            continue  # Skip native augmentation modules
        
        has_data, data_nodes = has_real_data_nodes(content)
        has_notif, notif_names = has_notifications(content)
        has_rpc_flag, rpc_names = has_rpcs(content)
        
        roles = []
        if has_data:
            roles.append('data')
        if has_notif:
            roles.append('notification')
        if has_rpc_flag:
            roles.append('rpc')
        
        if len(roles) > 1:
            specs = all_spec_modules.get(name, set())
            dual_modules.append((name, roles, data_nodes, notif_names, rpc_names, specs))

    print(f"=== CORRECTED DUAL-ROLE AUDIT ===")
    print(f"Modules with REAL multiple roles: {len(dual_modules)}")
    print()
    print(f"{'Module':<50s} {'Roles':<30s} {'Specs In':<25s} {'Status'}")
    print("-" * 120)

    missing_config = []
    missing_events = []
    missing_rpc = []

    for name, roles, data_nodes, notifs, rpcs, specs in dual_modules:
        missing = []
        if 'data' in roles and not specs.intersection({'cfg','other','native','oper','ietf','openconfig','mib'}):
            missing.append('data/config spec')
            missing_config.append(name)
        if 'notification' in roles and 'events' not in specs:
            missing.append('events spec')
            missing_events.append(name)
        if 'rpc' in roles and 'rpc' not in specs:
            missing.append('rpc spec')
            missing_rpc.append(name)
        
        status = 'MISSING: ' + ', '.join(missing) if missing else 'OK'
        print(f"  {name:<48s} {str(roles):<30s} {str(sorted(specs)):<25s} {status}")
        if data_nodes:
            print(f"    Data nodes: {', '.join(data_nodes[:5])}")

    print()
    print(f"=== SUMMARY ===")
    print(f"  Missing data/config specs: {len(missing_config)}")
    for m in missing_config:
        print(f"    - {m}")
    print(f"  Missing events specs: {len(missing_events)}")
    for m in missing_events:
        print(f"    - {m}")
    print(f"  Missing rpc specs: {len(missing_rpc)}")
    for m in missing_rpc:
        print(f"    - {m}")


if __name__ == '__main__':
    main()
