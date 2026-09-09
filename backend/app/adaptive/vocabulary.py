"""
Security Vocabulary - Known Security Concepts

This vocabulary defines the security meanings that the AI can recognize.
Each concept has multiple phrases that describe it.
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class SecurityConcept:
    """A security concept with its variations"""
    concept_id: str
    category: str
    normalized_field: str  # Path in Unified Security Model
    value: bool  # True = enabled, False = disabled
    phrases: List[str]
    description: str


# Security Vocabulary
SECURITY_VOCABULARY: Dict[str, SecurityConcept] = {
    "ssh_enabled": SecurityConcept(
        concept_id="ssh_enabled",
        category="Remote Access",
        normalized_field="remote_access.ssh_enabled",
        value=True,
        phrases=[
            "ssh enabled",
            "ssh access enabled",
            "secure shell enabled",
            "secure shell access",
            "ssh management enabled",
            "enable ssh",
            "remote ssh enabled",
            "ssh remote access",
            "secure remote shell",
            "management access secure-shell",
            "management ssh enabled",
            "secure-shell management",
            "ssh protocol enabled",
            "allow ssh access",
        ],
        description="SSH remote access is enabled"
    ),
    
    "ssh_disabled": SecurityConcept(
        concept_id="ssh_disabled",
        category="Remote Access",
        normalized_field="remote_access.ssh_enabled",
        value=False,
        phrases=[
            "ssh disabled",
            "ssh access disabled",
            "no ssh",
            "disable ssh",
            "ssh not allowed",
            "block ssh",
            "ssh denied",
        ],
        description="SSH remote access is disabled"
    ),
    
    "telnet_enabled": SecurityConcept(
        concept_id="telnet_enabled",
        category="Remote Access",
        normalized_field="remote_access.telnet_enabled",
        value=True,
        phrases=[
            "telnet enabled",
            "telnet access enabled",
            "enable telnet",
            "telnet management enabled",
            "remote telnet enabled",
            "telnet protocol enabled",
            "allow telnet access",
            "telnet remote access",
        ],
        description="Telnet remote access is enabled"
    ),
    
    "telnet_disabled": SecurityConcept(
        concept_id="telnet_disabled",
        category="Remote Access",
        normalized_field="remote_access.telnet_enabled",
        value=False,
        phrases=[
            "telnet disabled",
            "telnet access disabled",
            "no telnet",
            "disable telnet",
            "telnet not allowed",
            "block telnet",
            "telnet denied",
        ],
        description="Telnet remote access is disabled"
    ),
    
    "http_enabled": SecurityConcept(
        concept_id="http_enabled",
        category="Management",
        normalized_field="management.http_enabled",
        value=True,
        phrases=[
            "http enabled",
            "http server enabled",
            "web management http",
            "http management enabled",
            "enable http server",
            "http access enabled",
            "web server http",
        ],
        description="HTTP management is enabled"
    ),
    
    "http_disabled": SecurityConcept(
        concept_id="http_disabled",
        category="Management",
        normalized_field="management.http_enabled",
        value=False,
        phrases=[
            "http disabled",
            "no http server",
            "disable http",
            "http not allowed",
            "block http",
            "http denied",
        ],
        description="HTTP management is disabled"
    ),
    
    "https_enabled": SecurityConcept(
        concept_id="https_enabled",
        category="Management",
        normalized_field="management.https_enabled",
        value=True,
        phrases=[
            "https enabled",
            "https server enabled",
            "web management https",
            "https management enabled",
            "enable https server",
            "secure web management",
            "ssl web management",
            "tls web management",
        ],
        description="HTTPS management is enabled"
    ),
    
    "logging_enabled": SecurityConcept(
        concept_id="logging_enabled",
        category="Logging",
        normalized_field="logging.enabled",
        value=True,
        phrases=[
            "logging enabled",
            "audit logging enabled",
            "syslog enabled",
            "remote logging enabled",
            "log forwarding enabled",
            "audit forward",
            "send logs to server",
            "enable logging",
            "audit-forward",
        ],
        description="Security logging is enabled"
    ),
    
    "local_auth_enabled": SecurityConcept(
        concept_id="local_auth_enabled",
        category="Authentication",
        normalized_field="authentication.local_authentication",
        value=True,
        phrases=[
            "local authentication enabled",
            "local auth enabled",
            "local login enabled",
            "enable local authentication",
            "local user authentication",
            "local-auth enabled",
        ],
        description="Local authentication is enabled"
    ),
}


def get_all_concepts() -> List[SecurityConcept]:
    """Get all security concepts"""
    return list(SECURITY_VOCABULARY.values())


def get_concept_by_id(concept_id: str) -> SecurityConcept:
    """Get concept by ID"""
    return SECURITY_VOCABULARY.get(concept_id)


def get_all_phrases() -> List[str]:
    """Get all phrases from all concepts"""
    phrases = []
    for concept in SECURITY_VOCABULARY.values():
        phrases.extend(concept.phrases)
    return phrases
