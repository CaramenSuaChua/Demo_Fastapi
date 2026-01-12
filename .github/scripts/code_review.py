#!/usr/bin/env python3
"""
Script for GitHub Actions to review code changes using LLM API
"""

import os
import sys
import json
import requests
import subprocess
from typing import List, Dict, Any
from pathlib import Path

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LLM_API_URL = os.getenv("LLM_API_URL", "http://127.0.0.1:8000/api/review/")
PR_NUMBER = os.getenv("PR_NUMBER")
REPO = "https://github.com/CaramenSuaChua/Demo_Fastapi.git"

def get_changed_files() -> List[str]:
    """Get list of changed files in PR"""
    try:
        # Get diff between PR branch and target branch
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = result.stdout.strip().split('\n')
        return [f for f in files if f]  # Remove empty strings
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e}")
        return []

def get_file_content(file_path: str) -> str:
    """Get content of a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def get_file_diff(file_path: str) -> str:
    """Get diff of a specific file"""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD", "--", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting diff for {file_path}: {e}")
        return ""

def get_file_extension(file_path: str) -> str:
    """Get file extension"""
    return Path(file_path).suffix.lower()

def is_code_file(filename: str) -> bool:
    """Check if file is a code file"""
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
        '.hpp', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
        '.cs', '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte'
    }
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    # Check nếu là file đặc biệt (không có extension nhưng là code)
    if not extension:
        # Check for files without extension but known as code files
        filename_lower = filename.lower()
        if filename_lower in ['dockerfile', 'makefile', 'docker-compose.yml']:
            return True
        # Check if file starts with dot (hidden config files)
        if filename_lower.startswith('.'):
            return filename_lower not in ['.gitignore', '.env', '.env.example']
    
    return extension in code_extensions

def should_ignore_file(filename: str) -> bool:
    """Check if file should be ignored"""
    filename_lower = filename.lower()
    
    # Các pattern cần ignore
    ignore_list = [
        # Lock files
        'package-lock.json',
        'yarn.lock',
        'pnpm-lock.yaml',
        'poetry.lock',
        'pipfile.lock',
        'composer.lock',
        'gemfile.lock',
        
        # Minified files
        '.min.js',
        '.min.css',
        
        # Compiled/binary files
        '.pyc',
        '.pyo',
        '.pyd',
        '.so',
        '.dll',
        '.exe',
        '.dylib',
        '.class',
        '.jar',
        '.war',
        '.ear',
        
        # Log files
        '.log',
        
        # Temporary files
        '.tmp',
        '.temp',
        '.bak',
        '.swp',
        '.swo',
        
        # IDE files
        '.idea/',
        '.vscode/',
        '.vs/',
        
        # OS files
        '.ds_store',
        'thumbs.db',
        
        # Image/video files
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
        '.mp4', '.avi', '.mov', '.mkv',
        '.mp3', '.wav', '.ogg',
        
        # Font files
        '.ttf', '.otf', '.woff', '.woff2',
        
        # Archive files
        '.zip', '.tar', '.gz', '.7z', '.rar',
        
        # Document files
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    ]
    
    # Check các thư mục cần ignore
    if any(filename_lower.startswith(pattern) for pattern in [
        'node_modules/',
        'vendor/',
        'dist/',
        'build/',
        'out/',
        'target/',
        '__pycache__/',
        '.git/',
        '.github/',
        '.next/',
        '.nuxt/',
        '.output/',
        'coverage/',
        '.nyc_output/',
        '.pytest_cache/',
        '.mypy_cache/',
        '.ruff_cache/',
        '.venv/',
        'venv/',
        'env/',
        '.env',
        '.env.',
    ]):
        return True
    
    # Check các file cụ thể
    for pattern in ignore_list:
        if pattern.endswith('/'):
            if filename_lower.startswith(pattern[:-1]):
                return True
        elif pattern.startswith('.'):
            if filename_lower.endswith(pattern):
                return True
        elif filename_lower == pattern:
            return True
    
    return False

def call_llm_api(prompt: str) -> str:
    """Call LLM API for code review"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Actions-Code-Review'
        }
        
        payload = {
            'question': prompt
        }
        
        print(f"Calling LLM API at: {LLM_API_URL}")
        
        response = requests.post(
            LLM_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('answer', 'No review generated')
            else:
                return f"API Error: {result.get('error', 'Unknown error')}"
        else:
            return f"HTTP Error {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"Request Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

def format_review_for_pr(file_reviews: Dict[str, str]) -> str:
    """Format review results for PR comment"""
    if not file_reviews:
        return "✅ No code files changed or all changes are in non-code files."
    
    review_text = "### 📊 Code Review Summary\n\n"
    
    for file_path, review in file_reviews.items():
        if review.startswith("Error:"):
            review_text += f"#### 📄 {file_path}\n"
            review_text += f"❌ {review}\n\n"
        else:
            review_text += f"#### 📄 {file_path}\n"
            review_text += f"{review}\n\n"
    
    # Add summary
    total_files = len(file_reviews)
    reviewed_files = sum(1 for r in file_reviews.values() if not r.startswith("Error:"))
    
    review_text += "---\n"
    review_text += f"**📈 Summary**: Reviewed {reviewed_files}/{total_files} files\n\n"
    review_text += "💡 *This review is generated by AI. Please verify critical changes manually.*"
    
    return review_text

def main():
    """Main function"""
    print("🤖 Starting AI Code Review...")
    
    # Get changed files
    changed_files = get_changed_files()
    print(f"📁 Changed files: {len(changed_files)}")
    
    if not changed_files:
        print("No files changed. Exiting.")
        # Set output for GitHub Actions
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"has_review=false\n")
        sys.exit(0)
    
    # Filter code files
    code_files = [f for f in changed_files if is_code_file(f)]
    print(f"📝 Code files to review: {len(code_files)}")
    
    if not code_files:
        print("No code files to review.")
        # Set output for GitHub Actions
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"has_review=false\n")
            f.write(f"review_content=✅ No code files changed.\n")
        sys.exit(0)
    
    # Review each code file
    file_reviews = {}
    
    for file_path in code_files:
        print(f"🔍 Reviewing: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"  File not found: {file_path}")
            file_reviews[file_path] = "Error: File not found in workspace"
            continue
        
        # Get file content and diff
        content = get_file_content(file_path)
        diff = get_file_diff(file_path)
        
        if not content and not diff:
            print(f"  Skipping empty file: {file_path}")
            continue
        
        # Prepare prompt for LLM
        file_ext = get_file_extension(file_path)
        language = file_ext.replace('.', '')
        
        prompt = f"""
        Please review the following {language.upper()} code changes:
        
        FILE: {file_path}
        
        CODE CONTENT:
        ```
        {content[:5000]}  # Limit content length
        ```
        
        CHANGES (diff):
        ```
        {diff[:5000]}     # Limit diff length
        ```
        
        Please provide a code review focusing on:
        1. Code quality and readability
        2. Potential bugs or issues
        3. Performance considerations
        4. Security concerns
        5. Best practices violations
        6. Suggestions for improvement
        
        Keep the review concise and actionable.
        """
        
        # Call LLM API
        review = call_llm_api(prompt)
        file_reviews[file_path] = review
        
        print(f"  ✓ Review generated ({len(review)} chars)")
    
    # Format final review
    final_review = format_review_for_pr(file_reviews)
    
    # Set outputs for GitHub Actions
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"has_review=true\n")
        f.write(f"review_content={json.dumps(final_review)}\n")
    
    print("✅ Code review completed!")
    print(f"📋 Review length: {len(final_review)} characters")

if __name__ == "__main__":
    main()