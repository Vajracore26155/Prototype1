from .base import BaseParser, ParserError
from .cisco_parser import CiscoParser
from .fortinet_parser import FortinetParser
from .palo_alto_parser import PaloAltoParser
from .juniper_parser import JuniperParser
from .unknown_parser import UnknownParser


def parse_configuration(content: str, vendor: str):
    """
    Parse configuration content based on vendor
    
    Args:
        content: Configuration text
        vendor: Vendor name (Cisco, Fortinet, PaloAlto, Juniper, Unknown)
        
    Returns:
        Parsed configuration data
    """
    parser_map = {
        "Cisco": CiscoParser,
        "Fortinet": FortinetParser,
        "PaloAlto": PaloAltoParser,
        "Palo Alto": PaloAltoParser,
        "Juniper": JuniperParser,
        "Unknown": UnknownParser
    }
    
    parser_class = parser_map.get(vendor, UnknownParser)
    parser = parser_class()
    return parser.parse(content)


__all__ = [
    'BaseParser',
    'ParserError',
    'CiscoParser',
    'FortinetParser',
    'PaloAltoParser',
    'JuniperParser',
    'UnknownParser',
    'parse_configuration'
]
