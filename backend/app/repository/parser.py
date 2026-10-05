import ast
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SymbolInfo:
    def __init__(self, name: str, symbol_type: str, start_line: int, end_line: int, parent: Optional[str] = None, signature: Optional[str] = None):
        self.name = name
        self.symbol_type = symbol_type
        self.start_line = start_line
        self.end_line = end_line
        self.parent = parent
        self.signature = signature

    def qualified_name(self):
        if self.parent:
            return f"{self.parent}.{self.name}"
        return self.name

class DependencyInfo:
    def __init__(self, target: str, type: str = "import"):
        self.target = target
        self.type = type

class RepositoryParser:
    @staticmethod
    def parse_python(file_path: str, content: str) -> tuple[List[SymbolInfo], List[DependencyInfo]]:
        symbols = []
        dependencies = []
        try:
            tree = ast.parse(content, filename=file_path)
            
            class Visitor(ast.NodeVisitor):
                def __init__(self):
                    self.current_class = None

                def visit_Import(self, node):
                    for alias in node.names:
                        dependencies.append(DependencyInfo(target=alias.name, type="import"))
                        symbols.append(SymbolInfo(
                            name=alias.name,
                            symbol_type="import",
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno
                        ))
                    self.generic_visit(node)

                def visit_ImportFrom(self, node):
                    if node.module:
                        dependencies.append(DependencyInfo(target=node.module, type="import_from"))
                        for alias in node.names:
                            symbols.append(SymbolInfo(
                                name=alias.name,
                                symbol_type="import",
                                start_line=node.lineno,
                                end_line=node.end_lineno or node.lineno,
                                signature=node.module
                            ))
                    self.generic_visit(node)

                def visit_ClassDef(self, node):
                    symbols.append(SymbolInfo(
                        name=node.name,
                        symbol_type="class",
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno
                    ))
                    prev_class = self.current_class
                    self.current_class = node.name
                    self.generic_visit(node)
                    self.current_class = prev_class

                def visit_FunctionDef(self, node):
                    is_method = self.current_class is not None
                    
                    args = [a.arg for a in node.args.args]
                    signature = f"({', '.join(args)})"

                    symbols.append(SymbolInfo(
                        name=node.name,
                        symbol_type="method" if is_method else "function",
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        parent=self.current_class,
                        signature=signature
                    ))
                    # Do not enter function to prevent capturing inner functions unless we want them
                    # Actually we can use generic_visit if we want nested functions
                    # But for now let's just visit inner nodes for anything else
                    
            visitor = Visitor()
            visitor.visit(tree)

            return symbols, dependencies
        except SyntaxError as e:
            logger.warning(f"Syntax error parsing {file_path}: {e}")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return [], []
