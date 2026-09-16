"""
Configuration Cataloguing Script - Phase 0.5 Foundation
Analyzes all test configurations and creates data manifest with provenance
"""
import os
import json
import hashlib
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Calculate cryptographic hash of file"""
    hasher = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def detect_vendor_type(content: str, filename: str) -> tuple:
    """
    Attempt to detect vendor from configuration content
    Returns: (vendor, confidence, characteristics)
    """
    content_lower = content.lower()
    
    # Cisco indicators
    cisco_indicators = [
        'hostname', 'interface gigabitethernet', 'ip address',
        'router bgp', 'router ospf', 'access-list', 'crypto ipsec',
        'ip ssh version', 'line vty', 'enable secret'
    ]
    cisco_score = sum(1 for indicator in cisco_indicators if indicator in content_lower)
    
    # Fortinet indicators
    fortinet_indicators = [
        'config system', 'set allowaccess', 'edit', 'end',
        'config firewall', 'fortigate', 'fortios'
    ]
    fortinet_score = sum(1 for indicator in fortinet_indicators if indicator in content_lower)
    
    # Unknown/Custom indicators
    custom_indicators = [
        'management-access', 'device-name', 'remote-admin',
        'audit-forward', 'encrypted-shell', 'proprietary'
    ]
    custom_score = sum(1 for indicator in custom_indicators if indicator in content_lower)
    
    # Determine vendor
    if cisco_score >= 3:
        return ("Cisco", 0.8 + min(cisco_score * 0.02, 0.15), f"Cisco indicators: {cisco_score}")
    elif fortinet_score >= 2:
        return ("Fortinet", 0.7 + min(fortinet_score * 0.05, 0.25), f"Fortinet indicators: {fortinet_score}")
    elif custom_score >= 2:
        return ("Unknown/Synthetic", 0.6 + min(custom_score * 0.05, 0.3), f"Custom indicators: {custom_score}")
    else:
        return ("Unknown", 0.3, "Insufficient indicators")


def analyze_configuration(file_path: Path) -> Dict[str, Any]:
    """Analyze a single configuration file"""
    
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Calculate hash
        file_hash = calculate_file_hash(file_path)
        
        # Basic file info
        file_size = file_path.stat().st_size
        line_count = len(content.splitlines())
        
        # Detect vendor
        vendor, confidence, characteristics = detect_vendor_type(content, file_path.name)
        
        # Check for secrets/sensitive data markers
        has_redacted = '[REDACTED]' in content or '[MASKED]' in content
        
        # Determine if synthetic
        is_synthetic = any(marker in content for marker in [
            '# Unknown Vendor Configuration',
            '# Synthetic',
            'ProprietaryOS',
            'VendorXYZ',
            'DEMONSTRATION ONLY'
        ])
        
        # Extract any comments at the top (provenance info)
        first_lines = content.splitlines()[:10]
        comments = [line for line in first_lines if line.strip().startswith('#')]
        description = comments[0] if comments else None
        
        return {
            "filename": file_path.name,
            "file_path": str(file_path),
            "file_hash_sha256": file_hash,
            "file_size_bytes": file_size,
            "line_count": line_count,
            "vendor": vendor,
            "vendor_confidence": confidence,
            "vendor_detection_notes": characteristics,
            "is_synthetic": is_synthetic,
            "has_redacted_content": has_redacted,
            "description": description,
            "file_extension": file_path.suffix,
            "analyzed_at": datetime.utcnow().isoformat(),
            "status": "success"
        }
    
    except Exception as e:
        return {
            "filename": file_path.name,
            "file_path": str(file_path),
            "status": "error",
            "error": str(e),
            "analyzed_at": datetime.utcnow().isoformat()
        }


def catalogue_directory(directory: Path, recursive: bool = False) -> List[Dict[str, Any]]:
    """Catalogue all configuration files in a directory"""
    
    results = []
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    # Configuration file extensions
    config_extensions = ['.cfg', '.conf', '.txt', '.json', '.yaml', '.yml']
    
    for file_path in directory.glob(pattern):
        if file_path.is_file() and file_path.suffix in config_extensions:
            print(f"Analyzing: {file_path.name}")
            result = analyze_configuration(file_path)
            results.append(result)
    
    return results


def generate_manifest_json(results: List[Dict[str, Any]], output_path: Path):
    """Generate JSON manifest"""
    manifest = {
        "manifest_version": "1.0",
        "generated_at": datetime.utcnow().isoformat(),
        "total_files": len(results),
        "configurations": results
    }
    
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nGenerated JSON manifest: {output_path}")


def generate_manifest_csv(results: List[Dict[str, Any]], output_path: Path):
    """Generate CSV manifest"""
    if not results:
        return
    
    # Define CSV columns
    fieldnames = [
        "filename", "file_hash_sha256", "file_size_bytes", "line_count",
        "vendor", "vendor_confidence", "is_synthetic", "has_redacted_content",
        "file_extension", "status", "analyzed_at"
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Generated CSV manifest: {output_path}")


def print_summary(results: List[Dict[str, Any]]):
    """Print analysis summary"""
    total = len(results)
    successful = sum(1 for r in results if r['status'] == 'success')
    errors = total - successful
    
    if successful > 0:
        # Vendor distribution
        vendors = {}
        for r in results:
            if r['status'] == 'success':
                vendor = r['vendor']
                vendors[vendor] = vendors.get(vendor, 0) + 1
        
        # Synthetic vs real
        synthetic = sum(1 for r in results if r.get('is_synthetic', False))
        real = successful - synthetic
        
        # Redacted
        redacted = sum(1 for r in results if r.get('has_redacted_content', False))
        
        print("\n" + "=" * 60)
        print("CONFIGURATION CATALOGUE SUMMARY")
        print("=" * 60)
        print(f"Total files analyzed: {total}")
        print(f"Successful: {successful}")
        print(f"Errors: {errors}")
        print()
        print("Vendor Distribution:")
        for vendor, count in sorted(vendors.items(), key=lambda x: x[1], reverse=True):
            print(f"  {vendor}: {count} ({count/successful*100:.1f}%)")
        print()
        print(f"Synthetic configurations: {synthetic} ({synthetic/successful*100:.1f}%)")
        print(f"Real/public configurations: {real} ({real/successful*100:.1f}%)")
        print(f"Configurations with redacted content: {redacted}")
        print("=" * 60)


def main():
    """Main execution"""
    print("=" * 60)
    print("Vajra Core - Configuration Cataloguing Tool")
    print("Phase 0.5 Foundation")
    print("=" * 60)
    print()
    
    # Determine base path
    backend_path = Path(__file__).parent.parent
    data_path = backend_path / "data"
    
    # Directories to catalogue
    directories = [
        data_path / "sanitized",
        data_path / "uploads",
    ]
    
    # Create manifests directory
    manifests_dir = data_path / "manifests"
    manifests_dir.mkdir(exist_ok=True)
    
    all_results = []
    
    # Catalogue each directory
    for directory in directories:
        if directory.exists():
            print(f"\nCataloguing: {directory.name}/")
            print("-" * 60)
            results = catalogue_directory(directory, recursive=False)
            all_results.extend(results)
            print(f"Found {len(results)} configuration files")
        else:
            print(f"\nDirectory not found: {directory}")
    
    if not all_results:
        print("\nNo configuration files found!")
        return
    
    # Generate manifests
    print("\nGenerating manifests...")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    json_path = manifests_dir / f"manifest_{timestamp}.json"
    csv_path = manifests_dir / f"manifest_{timestamp}.csv"
    
    generate_manifest_json(all_results, json_path)
    generate_manifest_csv(all_results, csv_path)
    
    # Also create "latest" versions
    generate_manifest_json(all_results, manifests_dir / "manifest_latest.json")
    generate_manifest_csv(all_results, manifests_dir / "manifest_latest.csv")
    
    # Print summary
    print_summary(all_results)
    
    print("\nCataloguing complete!")


if __name__ == "__main__":
    main()
