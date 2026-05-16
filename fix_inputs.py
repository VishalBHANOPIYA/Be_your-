import os
import glob
import re

templates_dir = '/home/vish/Downloads/Be_your/app/templates'

for filepath in glob.glob(os.path.join(templates_dir, '**/*.html'), recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # We want to replace bg-surface with bg-input in input tags.
    # It's safer to just replace it generally where we see `class="...bg-surface...` inside input/textarea tags
    
    def replacer(match):
        return match.group(0).replace('bg-surface', 'bg-input')
        
    content = re.sub(r'<(input|textarea|select)[^>]*class="[^"]*"[^>]*>', replacer, content)
    
    with open(filepath, 'w') as f:
        f.write(content)

print("Inputs fixed!")
