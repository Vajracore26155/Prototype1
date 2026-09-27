#!/usr/bin/env python3
"""
Pre-flight check before starting the application

Verifies:
1. Database exists and tables are created
2. Required directories exist
3. Dependencies are installed
"""
import os
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="info"):
    """Print colored status message"""
    if status == "ok":
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    elif status == "error":
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
    else:
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")

def check_database():
    """Check if database exists and has tables"""
    try:
        from app.database import get_db_session, Configuration
        
        db_path = Path("data/sih26155.db")
        if not db_path.exists():
            print_status("Database file not found", "error")
            return False
        
        print_status(f"Database file exists: {db_path}", "ok")
        
        # Try to query configurations table
        db = get_db_session()
        try:
            count = db.query(Configuration).count()
            print_status(f"Database tables exist ({count} configurations found)", "ok")
            
            if count == 0:
                print_status("Database is empty - consider running populate script", "warning")
            
            return True
        except Exception as e:
            if "no such table" in str(e).lower():
                print_status("Database tables not initialized", "error")
                return False
            raise
        finally:
            db.close()
            
    except ImportError as e:
        print_status(f"Cannot import database module: {e}", "error")
        return False

def check_directories():
    """Check if required directories exist"""
    required_dirs = [
        "data",
        "data/uploads",
        "data/sanitized",
        "data/normalized",
        "data/reports"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_status(f"Directory exists: {dir_path}", "ok")
        else:
            print_status(f"Directory missing: {dir_path}", "warning")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check if key dependencies are installed"""
    required_packages = [
        ("fastapi", "FastAPI web framework"),
        ("sqlalchemy", "Database ORM"),
        ("pydantic", "Data validation"),
        ("uvicorn", "ASGI server"),
    ]
    
    all_installed = True
    for package, description in required_packages:
        try:
            __import__(package)
            print_status(f"{description}: {package}", "ok")
        except ImportError:
            print_status(f"{description}: {package} NOT INSTALLED", "error")
            all_installed = False
    
    return all_installed

def main():
    """Run all checks"""
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}SIH26155 Pre-Flight Setup Check{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")
    
    # Ensure we're in backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    checks = {
        "Dependencies": check_dependencies,
        "Directories": check_directories,
        "Database": check_database,
    }
    
    results = {}
    
    for check_name, check_func in checks.items():
        print(f"\n{Colors.BLUE}[{check_name}]{Colors.RESET}")
        results[check_name] = check_func()
    
    # Summary
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{status:8}{Colors.RESET} {check_name}")
    
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed! Ready to start application.{Colors.RESET}\n")
        print("Start the backend with:")
        print(f"  {Colors.BLUE}python -m uvicorn app.main:app --reload{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some checks failed. Please fix issues before starting.{Colors.RESET}\n")
        
        if not results.get("Database"):
            print("To initialize the database, run:")
            print(f"  {Colors.BLUE}python init_database.py{Colors.RESET}\n")
        
        if not results.get("Dependencies"):
            print("To install dependencies, run:")
            print(f"  {Colors.BLUE}pip install -r requirements.txt{Colors.RESET}\n")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
