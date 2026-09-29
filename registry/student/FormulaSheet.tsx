import React, { useState, useMemo } from 'react';

/**
 * @name FormulaSheet
 * @domain student
 * @description STEM mathematical and scientific formula quick-reference sheet with LaTeX representations, category filters, fast search, and one-click clipboard copying.
 * @capability formula-reference, math-physics, stem-cheat-sheet, scientific-calculus
 * @author Nexus Seed Registry Team
 */

export interface FormulaItem {
  id: string;
  name: string;
  category: 'Calculus' | 'Linear Algebra' | 'Physics' | 'Discrete Math' | 'Machine Learning';
  latex: string;
  description: string;
  variables: string[];
}

export interface FormulaSheetProps {
  initialFormulas?: FormulaItem[];
  defaultCategory?: string;
  onCopyFormula?: (item: FormulaItem) => void;
  className?: string;
}

const FORMULAS_DATA: FormulaItem[] = [
  {
    id: 'f1',
    name: "Euler's Formula",
    category: 'Calculus',
    latex: 'e^{i\\pi} + 1 = 0',
    description: 'Relates exponential function to complex numbers and trigonometry.',
    variables: ['e (base of natural log)', 'i (imaginary unit)', '\\pi (Archimedes constant)'],
  },
  {
    id: 'f2',
    name: 'Bayes Theorem',
    category: 'Discrete Math',
    latex: 'P(A|B) = \\frac{P(B|A) \\cdot P(A)}{P(B)}',
    description: 'Calculates conditional probability given prior knowledge and likelihood.',
    variables: ['P(A|B) = Posterior', 'P(B|A) = Likelihood', 'P(A) = Prior', 'P(B) = Evidence'],
  },
  {
    id: 'f3',
    name: 'Cosine Similarity',
    category: 'Machine Learning',
    latex: 'S_C(A, B) = \\frac{A \\cdot B}{\\|A\\| \\|B\\|} = \\frac{\\sum A_i B_i}{\\sqrt{\\sum A_i^2}\\sqrt{\\sum B_i^2}}',
    description: 'Measures angle between two non-zero vectors in inner product space.',
    variables: ['A, B (dense vectors)', '\\|A\\| (L2 norm)'],
  },
  {
    id: 'f4',
    name: 'Softmax Activation',
    category: 'Machine Learning',
    latex: '\\sigma(z)_i = \\frac{e^{z_i}}{\\sum_{j=1}^{K} e^{z_j}}',
    description: 'Normalizes input vector of K real numbers into probability distribution.',
    variables: ['z (logit vector)', 'K (class count)'],
  },
  {
    id: 'f5',
    name: 'Heisenberg Uncertainty Principle',
    category: 'Physics',
    latex: '\\Delta x \\cdot \\Delta p \\ge \\frac{\\hbar}{2}',
    description: 'Fundamental limit to precision of complementary quantum variables.',
    variables: ['\\Delta x (position uncertainty)', '\\Delta p (momentum uncertainty)', '\\hbar (reduced Planck constant)'],
  },
];

export const FormulaSheet: React.FC<FormulaSheetProps> = ({
  initialFormulas = FORMULAS_DATA,
  defaultCategory = 'All',
  onCopyFormula,
  className = '',
}) => {
  const [formulas] = useState<FormulaItem[]>(initialFormulas);
  const [search, setSearch] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>(defaultCategory);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const categories = useMemo(() => {
    const set = new Set(formulas.map((f) => f.category));
    return ['All', ...Array.from(set)];
  }, [formulas]);

  const filtered = useMemo(() => {
    return formulas.filter((f) => {
      const matchCat = selectedCategory === 'All' || f.category === selectedCategory;
      const matchSearch =
        search === '' ||
        f.name.toLowerCase().includes(search.toLowerCase()) ||
        f.description.toLowerCase().includes(search.toLowerCase()) ||
        f.latex.toLowerCase().includes(search.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [formulas, selectedCategory, search]);

  const copyToClipboard = (item: FormulaItem) => {
    navigator.clipboard.writeText(item.latex);
    setCopiedId(item.id);
    if (onCopyFormula) onCopyFormula(item);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-violet-400">STEM Formula Reference Catalog</h2>
          <p className="text-xs text-slate-400">Search mathematical theorems, formulas, and copy LaTeX code</p>
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-xs px-2.5 py-1 rounded-lg text-slate-300"
        >
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      <input
        type="text"
        placeholder="Search formulas by keyword (e.g. Cosine, Bayes, Softmax)..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-3 py-2 bg-slate-950/70 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-violet-500"
      />

      <div className="flex flex-col gap-3 max-h-[380px] overflow-y-auto pr-1">
        {filtered.map((item) => (
          <div
            key={item.id}
            className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl flex flex-col gap-2 hover:border-violet-500/50 transition-colors"
          >
            <div className="flex justify-between items-start">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-violet-950/70 text-violet-300">
                  {item.category}
                </span>
                <h3 className="text-sm font-semibold text-slate-200 mt-1">{item.name}</h3>
              </div>
              <button
                onClick={() => copyToClipboard(item)}
                className={`text-xs px-2.5 py-1 rounded-md font-medium transition-all ${
                  copiedId === item.id ? 'bg-emerald-600 text-white' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {copiedId === item.id ? 'Copied LaTeX!' : 'Copy LaTeX'}
              </button>
            </div>

            <div className="p-2.5 bg-slate-900 rounded-lg font-mono text-center text-sm text-violet-300 border border-slate-800/80 overflow-x-auto">
              {item.latex}
            </div>

            <p className="text-xs text-slate-400">{item.description}</p>
            <div className="flex flex-wrap gap-1 mt-1">
              {item.variables.map((v, i) => (
                <span key={i} className="text-[10px] px-1.5 py-0.5 bg-slate-800/80 rounded text-slate-400 font-mono">
                  {v}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FormulaSheet;
