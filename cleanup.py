import os
import shutil
import glob

def cleanup():
    print("Starting repository cleanup...")
    
    # 1. Walk directory tree and remove __pycache__, .pytest_cache, .pyc, .pyo, and .DS_Store files
    for root, dirs, files in os.walk('.'):
        # Exclude virtual environments
        if 'venv' in root or '.git' in root or 'venv_clean' in root:
            continue
            
        for d in list(dirs):
            if d in ('__pycache__', '.pytest_cache'):
                path = os.path.join(root, d)
                print(f"Removing directory: {path}")
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print(f"Error removing directory {path}: {e}")
                dirs.remove(d)
                
        for f in files:
            if f.endswith('.pyc') or f.endswith('.pyo') or f == '.DS_Store':
                path = os.path.join(root, f)
                print(f"Removing file: {path}")
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error removing file {path}: {e}")
                    
    # 2. Clean temporary logs and scripts (ignoring version controlled/active files)
    junk_patterns = [
        'tunnel*.log',
        'app.log',
        'logfile',
        'fix_inputs.py',
        'fix_styles.py',
        'verify_existing_users.py'
    ]
    for pattern in junk_patterns:
        for p in glob.glob(pattern):
            if os.path.isfile(p):
                print(f"Removing junk file: {p}")
                try:
                    os.remove(p)
                except Exception as e:
                    print(f"Error removing junk file {p}: {e}")
                    
    # 3. Clean database files EXCEPT the active sqlite file (be_your_db.db or inside instance/)
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or '.git' in root or 'venv_clean' in root:
            continue
        for f in files:
            if f.endswith('.db') and f != 'be_your_db.db':
                path = os.path.join(root, f)
                print(f"Removing inactive database file: {path}")
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error removing database file {path}: {e}")

    print("Repository cleanup complete!")

if __name__ == '__main__':
    cleanup()
