import React, { useState, useMemo } from 'react';

/**
 * @name CitationGenerator
 * @domain student
 * @description Academic bibliography and citation formatting tool generating APA 7th, MLA 9th, Chicago 17th, and IEEE citations from source metadata.
 * @capability citation-generator, bibliography, reference-formatter, apa-mla-ieee
 * @author Nexus Seed Registry Team
 */

export type CitationStyle = 'APA' | 'MLA' | 'IEEE' | 'Chicago';

export interface SourceMetadata {
  authors: string;
  title: string;
  publication: string;
  year: string;
  volume?: string;
  issue?: string;
  pages?: string;
  doi?: string;
}

export interface CitationGeneratorProps {
  initialMetadata?: SourceMetadata;
  defaultStyle?: CitationStyle;
  onCopyCitation?: (formatted: string, style: CitationStyle) => void;
  className?: string;
}

const DEFAULT_SOURCE: SourceMetadata = {
  authors: 'Zhong, L., & Hu, X.',
  title: 'Embedding Pipeline Optimization for Code Search and Component Retrieval',
  publication: 'arXiv preprint arXiv:2511.22240',
  year: '2025',
  doi: '10.48550/arXiv.2511.22240',
};

export const CitationGenerator: React.FC<CitationGeneratorProps> = ({
  initialMetadata = DEFAULT_SOURCE,
  defaultStyle = 'APA',
  onCopyCitation,
  className = '',
}) => {
  const [meta, setMeta] = useState<SourceMetadata>(initialMetadata);
  const [style, setStyle] = useState<CitationStyle>(defaultStyle);
  const [copied, setCopied] = useState<boolean>(false);

  const formattedCitation = useMemo(() => {
    const { authors, title, publication, year, volume, issue, pages, doi } = meta;
    const doiPart = doi ? ` https://doi.org/${doi.replace(/^https?:\/\/doi\.org\//, '')}` : '';

    switch (style) {
      case 'APA':
        return `${authors} (${year}). ${title}. ${publication}${volume ? `, ${volume}` : ''}${issue ? `(${issue})` : ''}${pages ? `, ${pages}` : ''}.${doiPart}`;
      case 'MLA':
        return `${authors}. "${title}." ${publication}${volume ? `, vol. ${volume}` : ''}${issue ? `, no. ${issue}` : ''}, ${year}${pages ? `, pp. ${pages}` : ''}.${doiPart}`;
      case 'IEEE':
        return `${authors}, "${title}," ${publication}${volume ? `, vol. ${volume}` : ''}${issue ? `, no. ${issue}` : ''}${pages ? `, pp. ${pages}` : ''}, ${year}.${doiPart}`;
      case 'Chicago':
        return `${authors}. "${title}." ${publication} ${volume || ''}${issue ? `, no. ${issue}` : ''} (${year})${pages ? `: ${pages}` : ''}.${doiPart}`;
      default:
        return '';
    }
  }, [meta, style]);

  const handleCopy = () => {
    navigator.clipboard.writeText(formattedCitation);
    setCopied(true);
    if (onCopyCitation) onCopyCitation(formattedCitation, style);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-amber-300">Academic Citation Generator</h2>
          <p className="text-xs text-slate-400">Generate formatted references for term papers and capstone theses</p>
        </div>
        <div className="flex gap-1 bg-slate-800 p-1 rounded-lg">
          {(['APA', 'MLA', 'IEEE', 'Chicago'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setStyle(s)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
                style === s ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 bg-slate-800/60 p-4 rounded-xl border border-slate-700/80">
        <div>
          <label className="text-xs text-slate-400 block mb-1">Author(s)</label>
          <input
            type="text"
            value={meta.authors}
            onChange={(e) => setMeta({ ...meta, authors: e.target.value })}
            className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 block mb-1">Year</label>
          <input
            type="text"
            value={meta.year}
            onChange={(e) => setMeta({ ...meta, year: e.target.value })}
            className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
          />
        </div>
        <div className="col-span-2">
          <label className="text-xs text-slate-400 block mb-1">Paper / Chapter Title</label>
          <input
            type="text"
            value={meta.title}
            onChange={(e) => setMeta({ ...meta, title: e.target.value })}
            className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 block mb-1">Journal / Conference / Publisher</label>
          <input
            type="text"
            value={meta.publication}
            onChange={(e) => setMeta({ ...meta, publication: e.target.value })}
            className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 block mb-1">DOI / URL</label>
          <input
            type="text"
            value={meta.doi || ''}
            onChange={(e) => setMeta({ ...meta, doi: e.target.value })}
            className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
            placeholder="10.1145/..."
          />
        </div>
      </div>

      <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl flex flex-col gap-3">
        <div className="flex justify-between items-center text-xs text-slate-400">
          <span className="font-semibold uppercase tracking-wider text-amber-400">{style} Output</span>
          <button
            onClick={handleCopy}
            className="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded font-medium transition-colors"
          >
            {copied ? 'Copied!' : 'Copy Reference'}
          </button>
        </div>
        <p className="text-sm font-serif italic text-slate-200 select-all leading-relaxed">
          {formattedCitation}
        </p>
      </div>
    </div>
  );
};

export default CitationGenerator;
