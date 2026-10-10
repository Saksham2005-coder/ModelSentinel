import os
import re

directory = 'c:/Users/Saksham Gupta/Desktop/ModelSentinel/frontend/src'

replacements = {
    r'bg-indigo-\d+ hover:bg-indigo-\d+ text-white': 'bg-brand hover:bg-brand-hover text-background-base',
    r'bg-indigo-\d+ hover:bg-indigo-\d+': 'bg-brand hover:bg-brand-hover text-background-base',
    r'text-indigo-\d+': 'text-brand',
    r'border-indigo-\d+': 'border-brand',
    r'bg-indigo-\d+/10': 'bg-brand-soft',
    r'bg-indigo-\d+/20': 'bg-brand-soft',
    r'bg-indigo-\d+/50': 'bg-brand-soft',
    
    r'text-emerald-\d+': 'text-status-success',
    r'bg-emerald-\d+ hover:bg-emerald-\d+': 'bg-status-success hover:bg-status-success/90 text-background-base',
    r'bg-emerald-\d+/10': 'bg-status-success-soft',
    r'border-emerald-\d+': 'border-status-success',
    r'border-emerald-\d+/50': 'border-status-success',
    
    r'text-rose-\d+': 'text-status-danger',
    r'bg-rose-\d+ hover:bg-rose-\d+': 'bg-status-danger hover:bg-status-danger/90 text-background-base',
    r'bg-rose-\d+/10': 'bg-status-danger-soft',
    r'bg-rose-\d+/20': 'bg-status-danger-soft',
    r'border-rose-\d+': 'border-status-danger',
    r'border-rose-\d+/20': 'border-status-danger',
    r'border-rose-\d+/50': 'border-status-danger',
    
    r'text-amber-\d+': 'text-status-warning',
    r'bg-amber-\d+ hover:bg-amber-\d+': 'bg-status-warning hover:bg-status-warning/90 text-background-base',
    r'bg-amber-\d+/10': 'bg-status-warning-soft',
    r'bg-amber-\d+/20': 'bg-status-warning-soft',
    r'border-amber-\d+': 'border-status-warning',
    
    r'bg-neutral-900': 'bg-background-base',
    r'bg-neutral-800': 'bg-background-secondary',
    r'bg-neutral-700': 'bg-background-elevated',
    r'border-neutral-800': 'border-border',
    r'border-neutral-700': 'border-border-strong',
    r'text-neutral-500': 'text-text-muted',
    r'text-neutral-400': 'text-text-secondary',
    r'text-neutral-300': 'text-text-primary',
    r'text-neutral-200': 'text-text-primary',
    r'text-neutral-100': 'text-text-primary',
    
    r'text-gray-500': 'text-text-muted',
    r'text-gray-400': 'text-text-secondary',
    r'text-gray-300': 'text-text-primary',
    r'text-gray-200': 'text-text-primary',
    r'text-gray-100': 'text-text-primary',
    r'bg-gray-900': 'bg-background-base',
    r'bg-gray-800': 'bg-background-secondary',
    r'bg-gray-700': 'bg-background-elevated',
    r'border-gray-800': 'border-border',
    r'border-gray-700': 'border-border-strong',
    
    # Custom specific matchers to clean up weird strings
    r'bg-status-danger hover:bg-status-danger/90 text-background-base text-text-primary': 'bg-status-danger hover:bg-status-danger/90 text-background-base',
    r'bg-status-success hover:bg-status-success/90 text-background-base text-text-primary': 'bg-status-success hover:bg-status-success/90 text-background-base',
    r'bg-brand hover:bg-brand-hover text-background-base text-text-primary': 'bg-brand hover:bg-brand-hover text-background-base',
}

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for pattern, repl in replacements.items():
                content = re.sub(pattern, repl, content)
                
            if content != original_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Updated {file}')
