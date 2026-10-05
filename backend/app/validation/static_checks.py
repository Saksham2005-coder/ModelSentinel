import os
import ast
from typing import List, Dict, Any

class StaticValidator:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        
    def check_syntax(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        errors = []
        for file_path in file_paths:
            full_path = os.path.join(self.repo_path, file_path)
            if not os.path.exists(full_path):
                continue
                
            if full_path.endswith(".py"):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    ast.parse(source)
                except SyntaxError as e:
                    errors.append({
                        "file": file_path,
                        "line": e.lineno,
                        "error": str(e)
                    })
                except Exception as e:
                    errors.append({
                        "file": file_path,
                        "error": str(e)
                    })
        return errors
