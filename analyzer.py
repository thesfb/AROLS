#!/usr/bin/env python3
"""
analyzer.py - Core code analysis engine
Usage: python3 analyzer.py <source_path> <output_path>
"""

import ast
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess

class CodeArcheologist:
    def __init__(self, source_path: str):
        self.source_path = Path(source_path)
        self.results = {
            "job_id": "",
            "project_name": self.source_path.name,
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
            "complexity_score": 0.0,
            "security_issues": [],
            "code_smells": [],
            "business_logic": [],
            "recommendations": [],
            "generated_at": datetime.now().isoformat()
        }
        
    def analyze(self) -> Dict[str, Any]:
        """Main analysis pipeline"""
        print(f"🔍 Starting analysis of {self.source_path}")
        
        # 1. File discovery and language detection
        self._discover_files()
        
        # 2. Code complexity analysis
        self._analyze_complexity()
        
        # 3. Security issue detection
        self._detect_security_issues()
        
        # 4. Code smell detection
        self._detect_code_smells()
        
        # 5. Business logic pattern extraction
        self._extract_business_logic()
        
        # 6. Generate recommendations
        self._generate_recommendations()
        
        print(f"✅ Analysis complete: {self.results['total_files']} files, {self.results['total_lines']} lines")
        return self.results
    
    def _discover_files(self):
        """Discover and categorize all code files"""
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.go': 'Go',
            '.java': 'Java',
            '.c': 'C',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.rs': 'Rust',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.sh': 'Shell',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.cob': 'COBOL',
            '.cbl': 'COBOL',
            '.for': 'Fortran'
        }
        
        for file_path in self.source_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                ext = file_path.suffix.lower()
                if ext in language_extensions:
                    lang = language_extensions[ext]
                    self.results['languages'][lang] = self.results['languages'].get(lang, 0) + 1
                    self.results['total_files'] += 1
                    
                    # Count lines
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len([line for line in f if line.strip()])
                            self.results['total_lines'] += lines
                    except Exception:
                        pass
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', '.venv', 'vendor', 'target', 'build', 'dist',
            '.idea', '.vscode', '.DS_Store'
        ]
        
        return any(pattern in str(file_path) for pattern in ignore_patterns)
    
    def _analyze_complexity(self):
        """Analyze code complexity using AST"""
        total_complexity = 0
        file_count = 0
        
        for py_file in self.source_path.rglob('*.py'):
            if self._should_ignore_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                    
                tree = ast.parse(source)
                complexity = self._calculate_cyclomatic_complexity(tree)
                total_complexity += complexity
                file_count += 1
                
                # Flag high complexity functions
                if complexity > 10:
                    self.results['code_smells'].append({
                        "type": "High Complexity",
                        "file": str(py_file.relative_to(self.source_path)),
                        "line": 1,
                        "description": f"File has cyclomatic complexity of {complexity}",
                        "suggestion": "Consider breaking down complex functions"
                    })
                    
            except Exception as e:
                print(f"Warning: Could not analyze {py_file}: {e}")
        
        if file_count > 0:
            self.results['complexity_score'] = round(total_complexity / file_count, 2)
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of AST"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _detect_security_issues(self):
        """Detect common security issues"""
        security_patterns = {
            'hardcoded_password': r'(password|pwd|pass)\s*=\s*["\'][^"\']+["\']',
            'sql_injection': r'(SELECT|INSERT|UPDATE|DELETE).*\+.*["\']',
            'hardcoded_secret': r'(secret|token|key)\s*=\s*["\'][^"\']{8,}["\']',
            'unsafe_eval': r'\beval\s*\(',
            'shell_injection': r'(os\.system|subprocess\.call|exec).*\+',
        }
        
        for file_path in self.source_path.rglob('*'):
            if file_path.suffix.lower() in ['.py', '.js', '.php', '.java', '.go']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines, 1):
                            for issue_type, pattern in security_patterns.items():
                                if re.search(pattern, line, re.IGNORECASE):
                                    severity = "High" if issue_type in ['sql_injection', 'shell_injection'] else "Medium"
                                    self.results['security_issues'].append({
                                        "type": issue_type.replace('_', ' ').title(),
                                        "severity": severity,
                                        "file": str(file_path.relative_to(self.source_path)),
                                        "line": i,
                                        "description": f"Potential {issue_type.replace('_', ' ')} found"
                                    })
                except Exception:
                    continue
    
    def _detect_code_smells(self):
        """Detect code smells and anti-patterns"""
        for py_file in self.source_path.rglob('*.py'):
            if self._should_ignore_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    line_stripped = line.strip()
                    
                    # Long lines
                    if len(line) > 120:
                        self.results['code_smells'].append({
                            "type": "Long Line",
                            "file": str(py_file.relative_to(self.source_path)),
                            "line": i,
                            "description": f"Line too long ({len(line)} characters)",
                            "suggestion": "Break line into multiple lines"
                        })
                    
                    # TODO comments (potential technical debt)
                    if 'TODO' in line_stripped or 'FIXME' in line_stripped:
                        self.results['code_smells'].append({
                            "type": "Technical Debt",
                            "file": str(py_file.relative_to(self.source_path)),
                            "line": i,
                            "description": "TODO/FIXME comment found",
                            "suggestion": "Address pending work item"
                        })
                    
                    # Magic numbers
                    magic_number_pattern = r'\b\d{2,}\b'
                    if re.search(magic_number_pattern, line_stripped) and not line_stripped.startswith('#'):
                        self.results['code_smells'].append({
                            "type": "Magic Number",
                            "file": str(py_file.relative_to(self.source_path)),
                            "line": i,
                            "description": "Magic number found",
                            "suggestion": "Replace with named constant"
                        })
                        
            except Exception:
                continue
    
    def _extract_business_logic(self):
        """Extract potential business logic patterns"""
        business_keywords = [
            'calculate', 'compute', 'process', 'validate', 'verify',
            'payment', 'invoice', 'order', 'customer', 'account',
            'price', 'discount', 'tax', 'billing', 'shipping',
            'user', 'login', 'authenticate', 'authorize', 'permission'
        ]
        
        for py_file in self.source_path.rglob('*.py'):
            if self._should_ignore_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                    
                tree = ast.parse(source)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name.lower()
                        
                        # Check if function name contains business keywords
                        for keyword in business_keywords:
                            if keyword in func_name:
                                self.results['business_logic'].append({
                                    "type": "Business Function",
                                    "file": str(py_file.relative_to(self.source_path)),
                                    "function": node.name,
                                    "description": f"Function appears to handle {keyword}-related logic",
                                    "value": "Potential API endpoint or business rule"
                                })
                                break
                        
                        # Check for validation patterns
                        if any(word in func_name for word in ['validate', 'check', 'verify']):
                            self.results['business_logic'].append({
                                "type": "Validation Logic",
                                "file": str(py_file.relative_to(self.source_path)),
                                "function": node.name,
                                "description": "Input validation or business rule validation",
                                "value": "Could be extracted into reusable validation service"
                            })
                            
            except Exception:
                continue
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Complexity recommendations
        if self.results['complexity_score'] > 8:
            recommendations.append("High code complexity detected. Consider refactoring complex functions into smaller, more manageable pieces.")
        
        # Security recommendations
        if len(self.results['security_issues']) > 0:
            high_security = len([issue for issue in self.results['security_issues'] if issue['severity'] == 'High'])
            if high_security > 0:
                recommendations.append(f"URGENT: {high_security} high-severity security issues found. Address immediately.")
            recommendations.append("Implement security scanning in your CI/CD pipeline.")
        
        # Business logic recommendations
        if len(self.results['business_logic']) > 5:
            recommendations.append("Significant business logic detected. Consider extracting into dedicated service layer or APIs.")
        
        # Language diversity
        if len(self.results['languages']) > 5:
            recommendations.append("Multiple programming languages detected. Consider consolidating or creating clear service boundaries.")
        
        # Code maintenance
        code_smell_count = len(self.results['code_smells'])
        if code_smell_count > 20:
            recommendations.append(f"{code_smell_count} code quality issues found. Implement linting and code review processes.")
        
        # Legacy indicators
        if 'COBOL' in self.results['languages'] or 'Fortran' in self.results['languages']:
            recommendations.append("Legacy languages detected. Plan modernization strategy to avoid technical debt.")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("Codebase appears well-maintained. Continue monitoring complexity and security.")
        
        self.results['recommendations'] = recommendations

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 analyzer.py <source_path> <output_path>")
        sys.exit(1)
    
    source_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(source_path):
        print(f"Error: Source path {source_path} does not exist")
        sys.exit(1)
    
    try:
        archaeologist = CodeArcheologist(source_path)
        results = archaeologist.analyze()
        
        # Write results to JSON file
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Analysis results written to {output_path}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()