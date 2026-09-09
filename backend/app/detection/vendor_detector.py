"""
Vendor Detection Engine
Deterministic fingerprinting for network device configurations
"""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class VendorType(str, Enum):
    """Supported vendor types"""
    CISCO = "Cisco"
    FORTINET = "Fortinet"
    AWS = "AWS"
    UNKNOWN = "Unknown"


@dataclass
class VendorSignature:
    """Signature pattern for vendor detection"""
    pattern: str
    weight: float  # Confidence weight (0.0 - 1.0)
    description: str
    flags: int = re.IGNORECASE


@dataclass
class DetectionResult:
    """Result of vendor detection"""
    vendor: VendorType
    confidence: float  # 0.0 - 1.0
    matched_signatures: List[str]
    scores: Dict[str, float]  # All vendor scores
    is_certain: bool  # confidence >= threshold


class VendorDetector:
    """
    Deterministic vendor detection using signature fingerprinting
    
    Detects:
    - Cisco IOS/IOS-XE
    - Fortinet FortiGate
    - AWS Security Groups (JSON)
    - Unknown (fallback)
    """
    
    def __init__(self, confidence_threshold: float = 0.75):
        """
        Initialize detector
        
        Args:
            confidence_threshold: Minimum confidence to classify as known vendor
        """
        self.confidence_threshold = confidence_threshold
        self.signatures = self._build_signatures()
    
    def _build_signatures(self) -> Dict[VendorType, List[VendorSignature]]:
        """Build vendor signature patterns"""
        
        return {
            VendorType.CISCO: [
                # High confidence indicators
                VendorSignature(
                    pattern=r'^\s*version\s+\d+\.\d+',
                    weight=0.3,
                    description="Cisco IOS version line",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*interface\s+(?:GigabitEthernet|FastEthernet|TenGigabitEthernet|Ethernet)',
                    weight=0.25,
                    description="Cisco interface naming",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*line\s+(?:vty|console|aux)',
                    weight=0.25,
                    description="Cisco line configuration",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*router\s+(?:ospf|eigrp|bgp|rip)',
                    weight=0.2,
                    description="Cisco routing protocol",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                
                # Medium confidence indicators
                VendorSignature(
                    pattern=r'^\s*ip\s+(?:route|address|ssh|http)',
                    weight=0.15,
                    description="Cisco IP commands",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*transport\s+input',
                    weight=0.15,
                    description="Cisco transport input",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*enable\s+(?:password|secret)',
                    weight=0.15,
                    description="Cisco enable secret",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*service\s+(?:password-encryption|tcp-keepalives)',
                    weight=0.1,
                    description="Cisco service commands",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                
                # Lower confidence indicators
                VendorSignature(
                    pattern=r'^\s*hostname\s+\S+',
                    weight=0.05,
                    description="Hostname (generic but common)",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*logging\s+\d+\.\d+\.\d+\.\d+',
                    weight=0.05,
                    description="Logging server",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
            ],
            
            VendorType.FORTINET: [
                # High confidence indicators
                VendorSignature(
                    pattern=r'^\s*config\s+(?:system|firewall|router|vpn)',
                    weight=0.35,
                    description="FortiGate config block",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*edit\s+["\']?\w+["\']?',
                    weight=0.25,
                    description="FortiGate edit command",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*set\s+\w+',
                    weight=0.2,
                    description="FortiGate set command",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*next\s*$',
                    weight=0.15,
                    description="FortiGate next command",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*end\s*$',
                    weight=0.1,
                    description="FortiGate end command",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                
                # Medium confidence indicators
                VendorSignature(
                    pattern=r'\ballowaccess\b',
                    weight=0.2,
                    description="FortiGate allowaccess",
                    flags=re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*config\s+system\s+interface',
                    weight=0.3,
                    description="FortiGate interface config",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'^\s*config\s+firewall\s+(?:policy|address)',
                    weight=0.25,
                    description="FortiGate firewall config",
                    flags=re.MULTILINE | re.IGNORECASE
                ),
                
                # Lower confidence indicators
                VendorSignature(
                    pattern=r'\bunset\s+\w+',
                    weight=0.1,
                    description="FortiGate unset command",
                    flags=re.IGNORECASE
                ),
            ],
            
            VendorType.AWS: [
                # JSON structure indicators
                VendorSignature(
                    pattern=r'"GroupId"\s*:',
                    weight=0.4,
                    description="AWS Security Group ID",
                    flags=re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'"IpPermissions"\s*:',
                    weight=0.3,
                    description="AWS IP Permissions",
                    flags=re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'"SecurityGroups"\s*:',
                    weight=0.3,
                    description="AWS Security Groups array",
                    flags=re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'"VpcId"\s*:',
                    weight=0.2,
                    description="AWS VPC ID",
                    flags=re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'"IpRanges"\s*:',
                    weight=0.15,
                    description="AWS IP Ranges",
                    flags=re.IGNORECASE
                ),
                VendorSignature(
                    pattern=r'"FromPort"\s*:',
                    weight=0.1,
                    description="AWS port configuration",
                    flags=re.IGNORECASE
                ),
            ]
        }
    
    def detect(self, content: str) -> DetectionResult:
        """
        Detect vendor from configuration content
        
        Args:
            content: Configuration file content
            
        Returns:
            DetectionResult with vendor, confidence, and matched signatures
        """
        # Calculate score for each vendor
        scores = {}
        matched_by_vendor = {}
        
        for vendor, signatures in self.signatures.items():
            score = 0.0
            matched = []
            
            for sig in signatures:
                if re.search(sig.pattern, content, sig.flags):
                    score += sig.weight
                    matched.append(sig.description)
            
            # Normalize score to 0-1 range (cap at 1.0)
            scores[vendor.value] = min(score, 1.0)
            matched_by_vendor[vendor] = matched
        
        # Determine winning vendor
        if not scores or max(scores.values()) == 0:
            # No matches - Unknown
            return DetectionResult(
                vendor=VendorType.UNKNOWN,
                confidence=0.0,
                matched_signatures=[],
                scores=scores,
                is_certain=False
            )
        
        # Find vendor with highest score
        winning_vendor_str = max(scores, key=scores.get)
        winning_vendor = VendorType(winning_vendor_str)
        confidence = scores[winning_vendor_str]
        
        # Determine if confident enough
        is_certain = confidence >= self.confidence_threshold
        
        # If not confident enough, classify as Unknown
        if not is_certain:
            return DetectionResult(
                vendor=VendorType.UNKNOWN,
                confidence=confidence,
                matched_signatures=matched_by_vendor.get(winning_vendor, []),
                scores=scores,
                is_certain=False
            )
        
        return DetectionResult(
            vendor=winning_vendor,
            confidence=confidence,
            matched_signatures=matched_by_vendor[winning_vendor],
            scores=scores,
            is_certain=True
        )
    
    def detect_vendor_name(self, content: str) -> Tuple[str, float]:
        """
        Convenience method that returns vendor name and confidence
        
        Returns:
            Tuple of (vendor_name, confidence)
        """
        result = self.detect(content)
        return result.vendor.value, result.confidence


def detect_vendor(content: str, confidence_threshold: float = 0.75) -> DetectionResult:
    """
    Convenience function to detect vendor
    
    Args:
        content: Configuration content
        confidence_threshold: Minimum confidence for known vendor classification
        
    Returns:
        DetectionResult
    """
    detector = VendorDetector(confidence_threshold=confidence_threshold)
    return detector.detect(content)


# Example usage and testing
if __name__ == "__main__":
    print("Testing Vendor Detection Engine")
    print("=" * 60)
    
    # Test Cisco configuration
    cisco_config = """
version 15.2
hostname CORE-01

interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0

line vty 0 4
 transport input ssh
 login local

router ospf 1
 network 192.168.1.0 0.0.0.255 area 0

ip ssh version 2
"""
    
    # Test Fortinet configuration
    fortinet_config = """
config system interface
    edit "wan1"
        set ip 192.168.1.1 255.255.255.0
        set allowaccess ping https ssh
    next
end

config firewall policy
    edit 1
        set name "allow-outbound"
        set srcintf "internal"
        set dstintf "wan1"
    next
end
"""
    
    # Test Unknown configuration
    unknown_config = """
device-name EDGE-01

management-access secure-shell

interface eth0
    address 192.168.1.1/24

audit-forward 10.10.10.10
"""
    
    detector = VendorDetector()
    
    # Test Cisco
    print("\n1. Testing Cisco Configuration:")
    result = detector.detect(cisco_config)
    print(f"   Vendor: {result.vendor.value}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Certain: {result.is_certain}")
    print(f"   Matched: {len(result.matched_signatures)} signatures")
    print(f"   Scores: {result.scores}")
    
    # Test Fortinet
    print("\n2. Testing Fortinet Configuration:")
    result = detector.detect(fortinet_config)
    print(f"   Vendor: {result.vendor.value}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Certain: {result.is_certain}")
    print(f"   Matched: {len(result.matched_signatures)} signatures")
    print(f"   Scores: {result.scores}")
    
    # Test Unknown
    print("\n3. Testing Unknown Configuration:")
    result = detector.detect(unknown_config)
    print(f"   Vendor: {result.vendor.value}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Certain: {result.is_certain}")
    print(f"   Matched: {len(result.matched_signatures)} signatures")
    print(f"   Scores: {result.scores}")
