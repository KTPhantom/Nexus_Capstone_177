# KSHITIJ'S 1-MINUTE GITHUB PUSH GUIDE

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
