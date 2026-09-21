"""
Configuration Differ
Phase 5: Configuration comparison utilities
"""
import difflib
from typing import Dict, List


def compare_configurations(baseline_content: str, current_content: str) -> Dict:
    """
    Compare two configuration file contents line-by-line
    
    Args:
        baseline_content: Baseline configuration text
        current_content: Current configuration text
        
    Returns:
        Dictionary with diff details
    """
    baseline_lines = baseline_content.splitlines()
    current_lines = current_content.splitlines()
    
    differ = difflib.Differ()
    diff = list(differ.compare(baseline_lines, current_lines))
    
    added_lines = [line[2:] for line in diff if line.startswith('+ ')]
    removed_lines = [line[2:] for line in diff if line.startswith('- ')]
    
    # Use unified diff for better readability
    unified_diff = difflib.unified_diff(
        baseline_lines,
        current_lines,
        lineterm='',
        fromfile='baseline',
        tofile='current'
    )
    
    return {
        "added_lines": added_lines,
        "removed_lines": removed_lines,
        "added_count": len(added_lines),
        "removed_count": len(removed_lines),
        "unified_diff": '\n'.join(unified_diff)
    }


def generate_diff(baseline_content: str, current_content: str, format: str = "unified") -> str:
    """
    Generate diff between two configurations
    
    Args:
        baseline_content: Baseline configuration
        current_content: Current configuration
        format: Diff format ("unified", "context", "ndiff")
        
    Returns:
        Formatted diff string
    """
    baseline_lines = baseline_content.splitlines(keepends=True)
    current_lines = current_content.splitlines(keepends=True)
    
    if format == "unified":
        diff = difflib.unified_diff(
            baseline_lines,
            current_lines,
            fromfile='baseline',
            tofile='current'
        )
    elif format == "context":
        diff = difflib.context_diff(
            baseline_lines,
            current_lines,
            fromfile='baseline',
            tofile='current'
        )
    elif format == "ndiff":
        diff = difflib.ndiff(baseline_lines, current_lines)
    else:
        diff = difflib.unified_diff(baseline_lines, current_lines)
    
    return ''.join(diff)
