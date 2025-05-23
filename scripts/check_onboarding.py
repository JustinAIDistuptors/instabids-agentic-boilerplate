#!/usr/bin/env python3
"""
Check onboarding status for AI agents.

This script verifies that all necessary components are in place
for AI agents to start development work.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class OnboardingChecker:
    """Check system readiness for AI agent development."""
    
    def __init__(self):
        self.project_root = project_root
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
    
    def check_environment(self) -> Tuple[bool, str]:
        """Check environment variables."""
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "GOOGLE_API_KEY"
        ]
        
        missing = []
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)
        
        if missing:
            return False, f"Missing environment variables: {', '.join(missing)}"
        return True, "All required environment variables set"
    
    def check_dependencies(self) -> Tuple[bool, str]:
        """Check Python dependencies."""
        try:
            import google.adk
            import google.genai
            import supabase
            return True, "All core dependencies installed"
        except ImportError as e:
            return False, f"Missing dependency: {e.name}"
    
    def check_adk_components(self) -> Tuple[bool, str]:
        """Check ADK components configuration."""
        components_path = self.project_root / ".adk" / "components.json"
        
        if not components_path.exists():
            return False, "Missing .adk/components.json"
        
        try:
            with open(components_path) as f:
                components = json.load(f)
            
            if "agents" not in components:
                return False, "No agents defined in components.json"
            
            agent_count = len(components["agents"])
            return True, f"Found {agent_count} agents in configuration"
        except Exception as e:
            return False, f"Error reading components.json: {e}"
    
    def check_prompts(self) -> Tuple[bool, str]:
        """Check prompt repository."""
        prompts_dir = self.project_root / ".prompts"
        
        if not prompts_dir.exists():
            return False, "Missing .prompts directory"
        
        required_dirs = ["system", "tasks", "conventions", "meta"]
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (prompts_dir / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return False, f"Missing prompt directories: {', '.join(missing_dirs)}"
        
        # Count prompt files
        prompt_count = sum(1 for _ in prompts_dir.rglob("*.md"))
        return True, f"Found {prompt_count} prompt files"
    
    def check_documentation(self) -> Tuple[bool, str]:
        """Check AI documentation."""
        docs_dir = self.project_root / "docs"
        
        required_docs = [
            "README_FOR_AI_CODERS.md",
            "COMMON_PITFALLS.md",
            "ADK_BEST_PRACTICES.md",
            "SUPABASE_PATTERNS.md"
        ]
        
        missing_docs = []
        for doc in required_docs:
            if not (docs_dir / doc).exists():
                missing_docs.append(doc)
        
        if missing_docs:
            self.warnings.append(f"Missing documentation: {', '.join(missing_docs)}")
            return True, "Documentation incomplete (non-critical)"
        
        return True, "All documentation present"
    
    def check_database_migrations(self) -> Tuple[bool, str]:
        """Check database migrations."""
        migrations_dir = self.project_root / "db" / "migrations"
        
        if not migrations_dir.exists():
            self.warnings.append("No database migrations found")
            return True, "Database migrations not set up (can be added later)"
        
        migration_count = sum(1 for _ in migrations_dir.glob("*.sql"))
        return True, f"Found {migration_count} database migrations"
    
    def run_all_checks(self) -> Dict[str, any]:
        """Run all onboarding checks."""
        checks = [
            ("Environment Variables", self.check_environment),
            ("Python Dependencies", self.check_dependencies),
            ("ADK Components", self.check_adk_components),
            ("Prompt Repository", self.check_prompts),
            ("Documentation", self.check_documentation),
            ("Database Migrations", self.check_database_migrations)
        ]
        
        results = {}
        
        print("\n🔍 Running Onboarding Checks...\n")
        
        for name, check_func in checks:
            success, message = check_func()
            results[name] = {"success": success, "message": message}
            
            if success:
                self.checks_passed += 1
                print(f"✅ {name}: {message}")
            else:
                self.checks_failed += 1
                print(f"❌ {name}: {message}")
        
        # Print summary
        print(f"\n📊 Summary: {self.checks_passed} passed, {self.checks_failed} failed\n")
        
        if self.warnings:
            print("⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")
            print()
        
        if self.checks_failed == 0:
            print("🎉 System ready for AI agent development!")
            print("\n📚 Next steps:")
            print("1. Review docs/README_FOR_AI_CODERS.md")
            print("2. Start with .prompts/tasks/create_llm_agent.md")
            print("3. Run 'poetry run adk web' to launch the dev UI")
        else:
            print("⚠️  Please fix the failed checks before proceeding.")
            print("\n🔧 Common fixes:")
            print("1. Run './scripts/reset_env.sh' to reset environment")
            print("2. Copy .env.template to .env and configure")
            print("3. Run 'poetry install' to install dependencies")
        
        return results


if __name__ == "__main__":
    checker = OnboardingChecker()
    results = checker.run_all_checks()
    
    # Exit with error code if any checks failed
    sys.exit(1 if checker.checks_failed > 0 else 0)