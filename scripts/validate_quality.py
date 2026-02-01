#!/usr/bin/env python3
"""
Quality Validation Script for Generated OpenAPI Specifications
Analyzes path coverage, schema completeness, and identifies sparse modules.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict

class QualityValidator:
    """Validate quality of generated OpenAPI specifications"""
    
    def __init__(self, swagger_root: str):
        self.swagger_root = Path(swagger_root)
        self.results = {
            'summary': {},
            'by_category': {},
            'sparse_modules': [],
            'rich_modules': [],
            'path_counts': {},
            'schema_counts': {}
        }
    
    def analyze_spec(self, spec_path: Path) -> Dict[str, Any]:
        """Analyze a single OpenAPI spec"""
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec = json.load(f)
            
            paths = spec.get('paths', {})
            schemas = spec.get('components', {}).get('schemas', {})
            
            # Count operations
            operations = 0
            for path, methods in paths.items():
                operations += len([m for m in methods.keys() if m in ['get', 'post', 'put', 'patch', 'delete']])
            
            # Analyze schema depth
            schema_properties = 0
            for schema_name, schema in schemas.items():
                schema_properties += self._count_properties(schema)
            
            return {
                'file': spec_path.name,
                'title': spec.get('info', {}).get('title', 'Unknown'),
                'paths': len(paths),
                'operations': operations,
                'schemas': len(schemas),
                'schema_properties': schema_properties,
                'avg_properties_per_schema': schema_properties / max(len(schemas), 1)
            }
        except Exception as e:
            return {
                'file': spec_path.name,
                'error': str(e),
                'paths': 0,
                'operations': 0,
                'schemas': 0,
                'schema_properties': 0
            }
    
    def _count_properties(self, schema: Dict, depth: int = 0) -> int:
        """Recursively count properties in a schema"""
        if depth > 10:
            return 0
            
        count = 0
        if 'properties' in schema:
            count += len(schema['properties'])
            for prop_name, prop_schema in schema['properties'].items():
                count += self._count_properties(prop_schema, depth + 1)
        
        if 'items' in schema and isinstance(schema['items'], dict):
            count += self._count_properties(schema['items'], depth + 1)
            
        return count
    
    def analyze_category(self, category_name: str, api_dir: Path) -> Dict[str, Any]:
        """Analyze all specs in a category directory"""
        if not api_dir.exists():
            return {'error': f'Directory not found: {api_dir}'}
        
        specs = []
        total_paths = 0
        total_operations = 0
        total_schemas = 0
        total_properties = 0
        
        for spec_file in sorted(api_dir.glob('*.json')):
            if spec_file.name in ['manifest.json', 'all-operations.json', 'all-configs.json', 
                                  'all-native.json', 'all-ietf.json', 'all-events.json',
                                  'all-openconfig.json', 'all-rpc.json', 'all-mib.json']:
                continue
                
            analysis = self.analyze_spec(spec_file)
            specs.append(analysis)
            
            total_paths += analysis.get('paths', 0)
            total_operations += analysis.get('operations', 0)
            total_schemas += analysis.get('schemas', 0)
            total_properties += analysis.get('schema_properties', 0)
            
            # Track sparse vs rich modules
            if analysis.get('paths', 0) < 5:
                self.results['sparse_modules'].append({
                    'category': category_name,
                    'file': analysis['file'],
                    'paths': analysis.get('paths', 0),
                    'schemas': analysis.get('schemas', 0)
                })
            elif analysis.get('paths', 0) > 20 and analysis.get('schemas', 0) > 10:
                self.results['rich_modules'].append({
                    'category': category_name,
                    'file': analysis['file'],
                    'paths': analysis.get('paths', 0),
                    'schemas': analysis.get('schemas', 0),
                    'properties': analysis.get('schema_properties', 0)
                })
        
        return {
            'category': category_name,
            'spec_count': len(specs),
            'total_paths': total_paths,
            'total_operations': total_operations,
            'total_schemas': total_schemas,
            'total_properties': total_properties,
            'avg_paths_per_spec': total_paths / max(len(specs), 1),
            'avg_schemas_per_spec': total_schemas / max(len(specs), 1)
        }
    
    def run_validation(self):
        """Run validation across all categories"""
        print("=" * 70)
        print("OpenAPI Specification Quality Validation")
        print("=" * 70)
        print()
        
        categories = [
            ('Operational', 'swagger-oper-model/api'),
            ('RPC', 'swagger-rpc-model/api'),
            ('Config', 'swagger-cfg-model/api'),
            ('OpenConfig', 'swagger-openconfig-model/api'),
            ('Native', 'swagger-native-config-model/api'),
            ('IETF', 'swagger-ietf-model/api'),
            ('Events', 'swagger-events-model/api'),
            ('MIB', 'swagger-mib-model/api'),
            ('Other', 'swagger-other-model/api')
        ]
        
        grand_total_specs = 0
        grand_total_paths = 0
        grand_total_ops = 0
        grand_total_schemas = 0
        
        print(f"{'Category':<15} {'Specs':>8} {'Paths':>8} {'Ops':>8} {'Schemas':>8} {'Avg Paths':>10}")
        print("-" * 70)
        
        for cat_name, cat_path in categories:
            api_dir = self.swagger_root / cat_path
            if api_dir.exists():
                result = self.analyze_category(cat_name, api_dir)
                self.results['by_category'][cat_name] = result
                
                grand_total_specs += result.get('spec_count', 0)
                grand_total_paths += result.get('total_paths', 0)
                grand_total_ops += result.get('total_operations', 0)
                grand_total_schemas += result.get('total_schemas', 0)
                
                print(f"{cat_name:<15} {result.get('spec_count', 0):>8} "
                      f"{result.get('total_paths', 0):>8} "
                      f"{result.get('total_operations', 0):>8} "
                      f"{result.get('total_schemas', 0):>8} "
                      f"{result.get('avg_paths_per_spec', 0):>10.1f}")
        
        print("-" * 70)
        print(f"{'TOTAL':<15} {grand_total_specs:>8} {grand_total_paths:>8} "
              f"{grand_total_ops:>8} {grand_total_schemas:>8}")
        
        self.results['summary'] = {
            'total_specs': grand_total_specs,
            'total_paths': grand_total_paths,
            'total_operations': grand_total_ops,
            'total_schemas': grand_total_schemas
        }
        
        # Report sparse modules
        print("\n" + "=" * 70)
        print("SPARSE MODULES (< 5 paths) - May Need Review")
        print("=" * 70)
        
        sparse_by_cat = defaultdict(list)
        for m in self.results['sparse_modules']:
            sparse_by_cat[m['category']].append(m)
        
        for cat, modules in sorted(sparse_by_cat.items()):
            print(f"\n{cat}: {len(modules)} sparse modules")
            for m in modules[:5]:  # Show first 5
                print(f"  - {m['file']}: {m['paths']} paths, {m['schemas']} schemas")
            if len(modules) > 5:
                print(f"  ... and {len(modules) - 5} more")
        
        # Report rich modules (examples of good generation)
        print("\n" + "=" * 70)
        print("TOP 10 RICHEST MODULES (Good Examples)")
        print("=" * 70)
        
        rich_sorted = sorted(self.results['rich_modules'], 
                            key=lambda x: x['paths'] + x['schemas'], reverse=True)[:10]
        
        for m in rich_sorted:
            print(f"  {m['category']}/{m['file']}: {m['paths']} paths, "
                  f"{m['schemas']} schemas, {m.get('properties', 0)} properties")
        
        return self.results
    
    def save_report(self, output_file: str):
        """Save validation report to JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nReport saved to: {output_file}")


def main():
    script_dir = Path(__file__).parent
    swagger_root = script_dir.parent
    
    validator = QualityValidator(str(swagger_root))
    results = validator.run_validation()
    
    # Save report
    report_file = swagger_root / 'archive' / 'quality_validation_report.json'
    validator.save_report(str(report_file))


if __name__ == '__main__':
    main()
