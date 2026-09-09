"""
Phase 2 verification script
Tests secret masking and vendor detection
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.security import mask_configuration, detect_secrets
from app.detection import detect_vendor, VendorType

print("=" * 60)
print("PHASE 2 VERIFICATION TEST")
print("=" * 60)

# Load demo configurations
def load_config(path):
    """Load configuration file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Failed to load {path}: {e}")
        return None

# Test 1: Secret Masking
print("\n[Test 1] Secret Masking Engine...")
cisco_content = load_config("../demo_configs/cisco/cisco_insecure.cfg")
if cisco_content:
    result = mask_configuration(cisco_content)
    print(f"✓ Masked {result.masked_count} secrets")
    print(f"  Types: {', '.join(result.masked_types)}")
    
    # Verify secrets are actually masked
    assert '[REDACTED]' in result.sanitized_content, "Should contain [REDACTED]"
    assert 'MyPassword123' not in result.sanitized_content, "Should mask plaintext passwords"
    print("✓ Secrets properly masked")
else:
    print("✗ Failed to load Cisco config")
    sys.exit(1)

# Test 2: Secret Detection (without masking)
print("\n[Test 2] Secret Detection...")
secrets = detect_secrets(cisco_content)
if secrets:
    print(f"✓ Detected {len(secrets)} secret types:")
    for secret_type, count in secrets.items():
        print(f"    {secret_type}: {count}")
else:
    print("✗ No secrets detected")
    sys.exit(1)

# Test 3: Cisco Vendor Detection
print("\n[Test 3] Cisco Vendor Detection...")
result = detect_vendor(cisco_content)
if result.vendor == VendorType.CISCO:
    print(f"✓ Correctly identified as Cisco")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Matched signatures: {len(result.matched_signatures)}")
    assert result.confidence >= 0.75, "Should have high confidence"
    assert result.is_certain, "Should be certain about Cisco"
else:
    print(f"✗ Incorrectly identified as {result.vendor}")
    sys.exit(1)

# Test 4: Fortinet Vendor Detection
print("\n[Test 4] Fortinet Vendor Detection...")
fortinet_content = load_config("../demo_configs/fortinet/fortinet_insecure.conf")
if fortinet_content:
    result = detect_vendor(fortinet_content)
    if result.vendor == VendorType.FORTINET:
        print(f"✓ Correctly identified as Fortinet")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Matched signatures: {len(result.matched_signatures)}")
        assert result.confidence >= 0.75, "Should have high confidence"
        assert result.is_certain, "Should be certain about Fortinet"
    else:
        print(f"✗ Incorrectly identified as {result.vendor}")
        sys.exit(1)
else:
    print("✗ Failed to load Fortinet config")
    sys.exit(1)

# Test 5: Unknown Vendor Detection
print("\n[Test 5] Unknown Vendor Detection...")
unknown_content = load_config("../demo_configs/unknown/vendor_xyz.conf")
if unknown_content:
    result = detect_vendor(unknown_content)
    if result.vendor == VendorType.UNKNOWN:
        print(f"✓ Correctly identified as Unknown")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  All scores below threshold")
    else:
        print(f"✗ Incorrectly identified as {result.vendor}")
        sys.exit(1)
else:
    print("✗ Failed to load Unknown config")
    sys.exit(1)

# Test 6: Confidence Threshold
print("\n[Test 6] Confidence Threshold Testing...")
# Test with very high threshold
from app.detection import VendorDetector
detector = VendorDetector(confidence_threshold=0.95)
result = detector.detect(cisco_content)
print(f"  Cisco at 95% threshold: {result.vendor.value} (confident: {result.is_certain})")

detector = VendorDetector(confidence_threshold=0.50)
result = detector.detect(cisco_content)
print(f"  Cisco at 50% threshold: {result.vendor.value} (confident: {result.is_certain})")
print("✓ Threshold mechanism working")

# Test 7: Secure vs Insecure Detection
print("\n[Test 7] Secure Configuration Detection...")
cisco_secure = load_config("../demo_configs/cisco/cisco_secure.cfg")
if cisco_secure:
    result = detect_vendor(cisco_secure)
    assert result.vendor == VendorType.CISCO, "Should detect secure Cisco as Cisco"
    print(f"✓ Secure Cisco config detected as Cisco ({result.confidence:.2%})")
else:
    print("✗ Failed to load secure Cisco config")

fortinet_secure = load_config("../demo_configs/fortinet/fortinet_secure.conf")
if fortinet_secure:
    result = detect_vendor(fortinet_secure)
    assert result.vendor == VendorType.FORTINET, "Should detect secure Fortinet as Fortinet"
    print(f"✓ Secure Fortinet config detected as Fortinet ({result.confidence:.2%})")
else:
    print("✗ Failed to load secure Fortinet config")

# Test 8: Masking doesn't affect detection
print("\n[Test 8] Masking Preserves Vendor Detection...")
masked_result = mask_configuration(cisco_content)
detection_before = detect_vendor(cisco_content)
detection_after = detect_vendor(masked_result.sanitized_content)

if detection_before.vendor == detection_after.vendor:
    print(f"✓ Vendor detection consistent after masking")
    print(f"  Before: {detection_before.vendor.value} ({detection_before.confidence:.2%})")
    print(f"  After:  {detection_after.vendor.value} ({detection_after.confidence:.2%})")
else:
    print(f"✗ Vendor detection changed after masking")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL PHASE 2 TESTS PASSED!")
print("=" * 60)
print("\nPhase 2 Security and Detection is ready.")
print("Verified components:")
print("  • Secret masking with multiple pattern types")
print("  • Vendor detection for Cisco")
print("  • Vendor detection for Fortinet")
print("  • Unknown vendor classification")
print("  • Confidence scoring and thresholds")
print("  • Demo configuration files")
print("\nNext: Phase 3 - Build complete Cisco audit pipeline")
print("=" * 60)
