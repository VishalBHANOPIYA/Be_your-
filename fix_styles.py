import os
import glob

templates_dir = '/home/vish/Downloads/Be_your/app/templates'

for filepath in glob.glob(os.path.join(templates_dir, '**/*.html'), recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace white/5 with surface
    content = content.replace('bg-white/5', 'bg-surface')
    content = content.replace('border-white/10', 'border-outline')
    content = content.replace('placeholder:text-white/20', 'placeholder:text-on-surface-variant')
    content = content.replace('text-white/40', 'text-on-surface-variant')
    content = content.replace('border-white/5', 'border-outline')
    content = content.replace('bg-surface-container', 'bg-surface')
    
    with open(filepath, 'w') as f:
        f.write(content)
print("Styles fixed in all templates!")
