"""Code generation and optimization agent for the Tío Pepe system."""

from typing import Dict, Any, List, Optional
import logging
import ast
import autopep8
import black
import re

class CodeAgent:
    """Specialized agent for code generation and optimization tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.supported_languages = ['python', 'javascript', 'typescript', 'java']

    def process_task(self, task: Any) -> Dict[str, Any]:
        """Process a code-related task based on its type."""
        task_type = task.data.get('code_type')
        code = task.data.get('code')
        language = task.data.get('language', 'python')

        if not code and task_type != 'generate':
            raise ValueError("No code provided for processing")

        if language.lower() not in self.supported_languages:
            raise ValueError(f"Unsupported programming language: {language}")

        if task_type == 'optimize':
            return self._optimize_code(code, language)
        elif task_type == 'analyze':
            return self._analyze_code(code, language)
        elif task_type == 'generate':
            template = task.data.get('template')
            requirements = task.data.get('requirements', [])
            return self._generate_code(template, requirements, language)
        else:
            raise ValueError(f"Unsupported code task type: {task_type}")

    def _optimize_code(self, code: str, language: str) -> Dict[str, Any]:
        """Optimize code for better readability and performance."""
        try:
            optimized_code = code
            if language.lower() == 'python':
                # Apply autopep8 formatting
                optimized_code = autopep8.fix_code(code, options={'aggressive': 1})
                # Apply black formatting
                optimized_code = black.format_str(optimized_code, mode=black.FileMode())

            # Remove unused imports and variables
            if language.lower() == 'python':
                optimized_code = self._remove_unused_imports(optimized_code)

            # Basic optimizations for other languages
            optimized_code = self._remove_redundant_whitespace(optimized_code)

            return {
                'optimized_code': optimized_code,
                'original_length': len(code),
                'optimized_length': len(optimized_code)
            }

        except Exception as e:
            self.logger.error(f"Code optimization error: {str(e)}")
            raise

    def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code for quality and potential issues."""
        try:
            analysis = {
                'metrics': self._calculate_code_metrics(code),
                'complexity': self._analyze_complexity(code, language),
                'style_issues': self._check_style_issues(code, language),
                'potential_bugs': self._detect_potential_bugs(code, language)
            }
            return {'analysis_results': analysis}

        except Exception as e:
            self.logger.error(f"Code analysis error: {str(e)}")
            raise

    def _generate_code(self, template: Optional[str], requirements: List[str], language: str) -> Dict[str, Any]:
        """Generate code based on template and requirements."""
        try:
            # Basic code generation based on templates and requirements
            generated_code = self._apply_template(template, requirements, language)
            
            # Optimize the generated code
            optimized_result = self._optimize_code(generated_code, language)
            
            return {
                'generated_code': optimized_result['optimized_code'],
                'template_used': bool(template),
                'requirements_met': len(requirements)
            }

        except Exception as e:
            self.logger.error(f"Code generation error: {str(e)}")
            raise

    def _calculate_code_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate various code metrics."""
        return {
            'total_lines': len(code.splitlines()),
            'code_lines': len([l for l in code.splitlines() if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in code.splitlines() if l.strip().startswith('#')]),
            'blank_lines': len([l for l in code.splitlines() if not l.strip()])
        }

    def _analyze_complexity(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code complexity."""
        if language.lower() == 'python':
            try:
                tree = ast.parse(code)
                return {
                    'num_functions': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                    'num_classes': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                    'max_depth': self._calculate_max_depth(tree)
                }
            except:
                return {'error': 'Unable to parse code for complexity analysis'}
        return {'error': 'Complexity analysis not supported for this language'}

    def _check_style_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Check for style issues in the code."""
        issues = []
        lines = code.splitlines()
        
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append({
                    'line': i,
                    'issue': 'Line too long',
                    'suggestion': 'Consider breaking the line into multiple lines'
                })
            if re.search(r'\s+$', line):
                issues.append({
                    'line': i,
                    'issue': 'Trailing whitespace',
                    'suggestion': 'Remove trailing whitespace'
                })

        return issues

    def _detect_potential_bugs(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Detect potential bugs in the code."""
        bugs = []
        if language.lower() == 'python':
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Except) and isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                        bugs.append({
                            'type': 'broad_exception',
                            'message': 'Avoid catching broad exceptions',
                            'suggestion': 'Catch specific exceptions instead'
                        })
            except:
                bugs.append({
                    'type': 'syntax_error',
                    'message': 'Code contains syntax errors',
                    'suggestion': 'Fix syntax errors before analysis'
                })
        return bugs

    def _remove_unused_imports(self, code: str) -> str:
        """Remove unused imports from Python code."""
        try:
            tree = ast.parse(code)
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
            
            lines = code.splitlines()
            return '\n'.join(line for line in lines 
                            if not any(imp.lineno == i + 1 for imp in imports 
                                    if not any(name in used_names for name in self._get_import_names(imp))))
        except:
            return code

    def _get_import_names(self, node: ast.AST) -> List[str]:
        """Get names imported by an import node."""
        if isinstance(node, ast.Import):
            return [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            return [alias.name for alias in node.names]
        return []

    def _remove_redundant_whitespace(self, code: str) -> str:
        """Remove redundant whitespace from code."""
        lines = code.splitlines()
        # Remove trailing whitespace
        lines = [line.rstrip() for line in lines]
        # Remove multiple blank lines
        result = []
        prev_empty = False
        for line in lines:
            if not line.strip():
                if not prev_empty:
                    result.append(line)
                prev_empty = True
            else:
                result.append(line)
                prev_empty = False
        return '\n'.join(result)

    def _apply_template(self, template: Optional[str], requirements: List[str], language: str) -> str:
        """Apply a template with given requirements to generate code."""
        if template:
            return template  # Use provided template as base
        
        # Generate basic code structure based on requirements
        if language.lower() == 'python':
            return self._generate_python_code(requirements)
        elif language.lower() == 'javascript':
            return self._generate_javascript_code(requirements)
        else:
            return f"// Generated code for {language}\n// Add implementation here"

    def _generate_python_code(self, requirements: List[str]) -> str:
        """Generate Python code based on requirements."""
        code = ['''#!/usr/bin/env python3
"""Generated code based on requirements."""

''']
        
        # Add imports
        if 'async' in str(requirements).lower():
            code.append('import asyncio')
        if 'http' in str(requirements).lower():
            code.append('import aiohttp')
        
        # Add main class or function
        if 'class' in str(requirements).lower():
            code.append('\nclass MainClass:')
            code.append('    def __init__(self):')
            code.append('        pass\n')
        else:
            code.append('\ndef main():')
            code.append('    pass\n')
        
        # Add entry point
        code.append("if __name__ == '__main__':")
        code.append('    main()')
        
        return '\n'.join(code)

    def _generate_javascript_code(self, requirements: List[str]) -> str:
        """Generate JavaScript code based on requirements."""
        code = ['// Generated code based on requirements\n']
        
        # Add imports
        if 'async' in str(requirements).lower():
            code.append('const util = require("util");')
        
        # Add main class or function
        if 'class' in str(requirements).lower():
            code.append('\nclass MainClass {')
            code.append('    constructor() {')
            code.append('    }\n}')
        else:
            code.append('\nfunction main() {')
            code.append('}\n')
        
        # Add execution
        code.append('main();')
        
        return '\n'.join(code)

    def _calculate_max_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth in Python code."""
        max_depth = 0
        current_depth = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While, ast.If, ast.With)):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif isinstance(node, ast.FunctionDef):
                current_depth = 0

        return max_depth

    def cleanup(self) -> None:
        """Cleanup resources used by the agent."""
        self.logger.info("Code agent cleaned up")