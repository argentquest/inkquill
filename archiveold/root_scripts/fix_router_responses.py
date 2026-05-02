#!/usr/bin/env python3
"""
Automated script to fix router responses to wrap them in ApiResponse.

This script:
1. Identifies routers that need fixing
2. Analyzes return statements
3. Wraps responses in ApiResponse.success_response()
4. Ensures proper imports

Usage:
    python fix_router_responses.py --dry-run  # Preview changes
    python fix_router_responses.py --file app/routers/story.py  # Fix single file
    python fix_router_responses.py --all  # Fix all routers
"""

import re
import os
import argparse
from pathlib import Path
from typing import List, Tuple, Set


class RouterFixer:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.fixed_count = 0
        self.error_count = 0

    def has_api_response_import(self, content: str) -> bool:
        """Check if ApiResponse is already imported."""
        return re.search(r'from app\.schemas\.base import.*ApiResponse', content) is not None

    def add_api_response_import(self, content: str) -> str:
        """Add ApiResponse import if not present."""
        if self.has_api_response_import(content):
            # Check for duplicate imports and clean them up
            lines = content.split('\n')
            import_lines = []
            other_lines = []
            api_response_found = False

            for line in lines:
                if 'from app.schemas.base import' in line and 'ApiResponse' in line:
                    if not api_response_found:
                        # Keep first import, ensure ApiMeta is also imported
                        if 'ApiMeta' not in line:
                            line = line.rstrip()
                            if line.endswith('ApiResponse'):
                                line += ', ApiMeta'
                            else:
                                line = line.replace('ApiResponse', 'ApiResponse, ApiMeta')
                        import_lines.append(line)
                        api_response_found = True
                    # Skip duplicate imports
                else:
                    other_lines.append(line)

            return '\n'.join(import_lines + other_lines)

        # Add import after other schema imports
        lines = content.split('\n')
        insert_index = 0

        for i, line in enumerate(lines):
            if line.startswith('from app.schemas'):
                insert_index = i + 1
            elif line.startswith('from app.crud') or line.startswith('from app.core'):
                if insert_index == 0:
                    insert_index = i
                break

        lines.insert(insert_index, 'from app.schemas.base import ApiResponse, ApiMeta')
        return '\n'.join(lines)

    def find_unwrapped_returns(self, content: str) -> List[Tuple[int, str]]:
        """Find return statements that need wrapping."""
        lines = content.split('\n')
        unwrapped_returns = []

        in_function = False
        function_has_api_response = False

        for i, line in enumerate(lines):
            # Check if we're entering a function with ApiResponse response_model
            if '@router.' in line:
                # Look ahead for response_model=ApiResponse
                for j in range(i, min(i + 5, len(lines))):
                    if 'response_model=ApiResponse' in lines[j]:
                        function_has_api_response = True
                        break
                    if 'async def ' in lines[j] or 'def ' in lines[j]:
                        break

            if 'async def ' in line or 'def ' in line:
                in_function = True

            # Check return statements
            if in_function and function_has_api_response and line.strip().startswith('return '):
                # Skip if already wrapped
                if 'ApiResponse.success_response' in line or 'ApiResponse.error_response' in line:
                    continue

                # Skip if returning Response object (like 204 No Content)
                if 'Response(status_code=' in line:
                    continue

                # Skip if raising exception
                if 'raise ' in line:
                    continue

                # Skip if returning dict with message/error (might be intentional)
                if re.search(r'return\s*\{.*["\']message["\'].*\}', line):
                    # These might need wrapping, add to list
                    unwrapped_returns.append((i, line))
                    continue

                # This return likely needs wrapping
                unwrapped_returns.append((i, line))

            # Reset function tracking
            if in_function and line and not line[0].isspace() and '@router' not in line:
                in_function = False
                function_has_api_response = False

        return unwrapped_returns

    def wrap_return_statement(self, line: str) -> str:
        """Wrap a return statement in ApiResponse.success_response()."""
        # Extract the return value
        match = re.match(r'(\s*)return\s+(.+)', line)
        if not match:
            return line

        indent = match.group(1)
        value = match.group(2).rstrip()

        # Handle different return types
        if value == 'None' or value == 'null':
            return f'{indent}return ApiResponse.success_response(data=None)'

        # If it's already a dict, wrap it
        if value.startswith('{'):
            return f'{indent}return ApiResponse.success_response(data={value})'

        # If it's a variable or model instance
        return f'{indent}return ApiResponse.success_response(data={value})'

    def fix_file(self, file_path: Path) -> bool:
        """Fix a single router file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Add imports if needed
            content = self.add_api_response_import(content)

            # Find unwrapped returns
            unwrapped = self.find_unwrapped_returns(content)

            if not unwrapped:
                print(f"✓ {file_path.name}: No changes needed")
                return True

            # Apply fixes (from bottom to top to preserve line numbers)
            lines = content.split('\n')
            for line_num, original_line in reversed(unwrapped):
                new_line = self.wrap_return_statement(original_line)
                lines[line_num] = new_line
                print(f"  Line {line_num + 1}: {original_line.strip()} -> {new_line.strip()}")

            content = '\n'.join(lines)

            if self.dry_run:
                print(f"🔍 {file_path.name}: Would fix {len(unwrapped)} return statements")
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ {file_path.name}: Fixed {len(unwrapped)} return statements")
                self.fixed_count += 1

            return True

        except Exception as e:
            print(f"❌ {file_path.name}: Error - {e}")
            self.error_count += 1
            return False

    def get_router_files(self) -> List[Path]:
        """Get list of all router files."""
        routers_dir = Path('app/routers')
        if not routers_dir.exists():
            print(f"❌ Routers directory not found: {routers_dir}")
            return []

        # Exclude views_* files as they will be removed
        router_files = [
            f for f in routers_dir.glob('*.py')
            if f.name not in ['__init__.py'] and not f.name.startswith('views_')
        ]

        return sorted(router_files)


def main():
    parser = argparse.ArgumentParser(description='Fix router responses to wrap in ApiResponse')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--file', type=str, help='Fix specific file')
    parser.add_argument('--all', action='store_true', help='Fix all router files')

    args = parser.parse_args()

    fixer = RouterFixer(dry_run=args.dry_run)

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1

        fixer.fix_file(file_path)

    elif args.all:
        router_files = fixer.get_router_files()
        print(f"\n{'=' * 60}")
        print(f"Found {len(router_files)} router files to process")
        print(f"Mode: {'DRY RUN (preview only)' if args.dry_run else 'LIVE (will modify files)'}")
        print(f"{'=' * 60}\n")

        for router_file in router_files:
            fixer.fix_file(router_file)

        print(f"\n{'=' * 60}")
        print(f"Summary:")
        print(f"  Fixed: {fixer.fixed_count}")
        print(f"  Errors: {fixer.error_count}")
        print(f"  Total: {len(router_files)}")
        print(f"{'=' * 60}\n")

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
