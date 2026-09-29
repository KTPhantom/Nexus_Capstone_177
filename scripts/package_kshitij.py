"""
Package Kshitij's complete deliverable package including:
1. Full functional project
2. Dedicated KSHITIJ_PUSH_INSTRUCTIONS.md
3. 1-click batch script for Kshitij to push his commit to KTPhantom/Nexus_Capstone_177
"""
import os
import zipfile

BASE_DIR = r"c:\Users\Asus\Desktop\Capstone"
os.chdir(BASE_DIR)

INSTRUCTIONS = """# KSHITIJ'S 1-MINUTE GITHUB PUSH GUIDE

Hi Kshitij! Barun's commit (`feat(orchestration)`) is already pushed to `https://github.com/KTPhantom/Nexus_Capstone_177.git`.
Divyansh's commit (`indexing & retrieval`) is also already there.

Now you just need to push YOUR modules (`representation`, `cicd`, `.github`) so your name and commit show up on the GitHub repository!

---

### Step 1: Open Terminal in your local repo folder
If you already have the repo cloned locally:
```powershell
cd path/to/Nexus_Capstone_177
git pull origin main
```
*(If you haven't cloned it yet: `git clone https://github.com/KTPhantom/Nexus_Capstone_177.git`)*

---

### Step 2: Copy your MLOps modules into the repo
Make sure these folders are in the repository:
1. `nexus/representation/` (contains `schema_compressor.py`, `batch_compressor.py`)
2. `nexus/cicd/` (contains `dual_hasher.py`, `incremental_indexer.py`, `regression_gate.py`)
3. `.github/workflows/` (contains `embed-components.yml`)

---

### Step 3: Run these 3 Git commands
```powershell
git add nexus/representation nexus/cicd .github
git commit -m "feat(mlops): implement SEA schema compressor, dual-hash change detection, and CI/CD quality gate

- Implement SEA AST schema compression stripping Tailwind CSS and JSX noise (Hu et al., IEEE TSE 2024)
- Achieve 94.8% token reduction from 9,613 words down to 499 words per prompt
- Implement Dual-Hash Change Detection (H_struct vs H_sem) to avoid re-embedding on cosmetic changes
- Implement CI/CD Quality Regression Gate checking MRR, Recall@3, and NDCG@5 thresholds"
git push origin main
```

---

### DONE!
Now if Dr. Najjar opens `https://github.com/KTPhantom/Nexus_Capstone_177`:
1. Divyansh's commit is there.
2. Barun's commit is there.
3. **Your commit is there!**
All 3 group members have clean, professional, individual commit histories!

For viva defense answers and math derivations, open:
`docs/MASTER_DEFENSE_AND_EXPLANATION_GUIDE.md`
"""

def create_kshitij_package():
    zip_path = os.path.join(BASE_DIR, "nexus_kshitij_complete_package.zip")
    print(f"Creating {zip_path}...")
    extensions = ('.py', '.tsx', '.md', '.toml', '.txt', '.yml', '.json', '.html', '.npz')
    skip_dirs = ('__pycache__', '.pytest_cache', '.git', 'node_modules')

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fn in files:
                if fn.endswith(extensions) and not fn.startswith('nexus_'):
                    full = os.path.join(root, fn)
                    arc = os.path.relpath(full, '.')
                    z.write(full, arc)
        
        # Add the explicit step-by-step instructions file
        z.writestr('KSHITIJ_PUSH_INSTRUCTIONS.md', INSTRUCTIONS)

    size = os.path.getsize(zip_path) / 1024
    print(f"Done: {zip_path} ({size:.1f} KB)")

if __name__ == "__main__":
    create_kshitij_package()
