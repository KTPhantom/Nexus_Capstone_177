import React, { useState, useEffect, useMemo } from 'react';

/**
 * @name NotesEditor
 * @domain student
 * @description Rich markdown notes editor with live preview toggle, word and character counters, subject tagging, auto-save status indicator, and plain text export.
 * @capability notes-editor, markdown, study-notes, document-management
 * @author Nexus Seed Registry Team
 */

export interface NoteDocument {
  id: string;
  title: string;
  subject: string;
  content: string;
  updatedAt: string;
}

export interface NotesEditorProps {
  initialDocument?: NoteDocument;
  onSave?: (note: NoteDocument) => void;
  className?: string;
}

const DEFAULT_NOTE: NoteDocument = {
  id: 'note-101',
  title: 'Distributed Systems: Paxos vs Raft Summary',
  subject: 'CS301',
  content: `# Paxos vs Raft Overview\n\n- **Paxos**: Proven theoretical safety, but notorious for implementation complexity.\n- **Raft**: Designed specifically for understandability with explicit leader election, log replication, and safety invariants.\n\n### Key Terms\n1. State Machine Replication\n2. Majority Quorum: (N/2) + 1\n3. Term numbering & heartbeats`,
  updatedAt: new Date().toISOString(),
};

export const NotesEditor: React.FC<NotesEditorProps> = ({
  initialDocument = DEFAULT_NOTE,
  onSave,
  className = '',
}) => {
  const [doc, setDoc] = useState<NoteDocument>(initialDocument);
  const [isPreview, setIsPreview] = useState<boolean>(false);
  const [isSaved, setIsSaved] = useState<boolean>(true);

  const { wordCount, charCount } = useMemo(() => {
    const text = doc.content.trim();
    const words = text ? text.split(/\s+/).length : 0;
    return {
      wordCount: words,
      charCount: text.length,
    };
  }, [doc.content]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsSaved(true);
      if (onSave) onSave(doc);
    }, 1500);
    return () => clearTimeout(timer);
  }, [doc, onSave]);

  const handleChange = (field: keyof NoteDocument, val: string) => {
    setIsSaved(false);
    setDoc((prev) => ({
      ...prev,
      [field]: val,
      updatedAt: new Date().toISOString(),
    }));
  };

  const handleExport = () => {
    const blob = new Blob([doc.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${doc.title.replace(/\s+/g, '_')}.md`;
    link.click();
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-4 max-w-2xl w-full ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1 mr-4">
          <input
            type="text"
            value={doc.title}
            onChange={(e) => handleChange('title', e.target.value)}
            className="text-xl font-bold bg-transparent border-b border-transparent hover:border-slate-700 focus:border-indigo-500 focus:outline-none w-full text-indigo-300"
          />
          <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
            <input
              type="text"
              value={doc.subject}
              onChange={(e) => handleChange('subject', e.target.value)}
              className="bg-slate-800 px-2 py-0.5 rounded font-mono text-indigo-400 w-24 focus:outline-none"
              placeholder="Tag / Subject"
            />
            <span>{isSaved ? '✓ Auto-saved' : '● Saving...'}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPreview(!isPreview)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-lg text-slate-300 border border-slate-700"
          >
            {isPreview ? 'Edit Mode' : 'Preview'}
          </button>
          <button
            onClick={handleExport}
            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold rounded-lg text-white"
          >
            Export .md
          </button>
        </div>
      </div>

      {isPreview ? (
        <div className="min-h-[260px] p-4 bg-slate-950/70 border border-slate-800 rounded-xl text-sm leading-relaxed whitespace-pre-wrap font-sans text-slate-200">
          {doc.content}
        </div>
      ) : (
        <textarea
          value={doc.content}
          onChange={(e) => handleChange('content', e.target.value)}
          className="min-h-[260px] p-4 bg-slate-950/70 border border-slate-800 focus:border-indigo-500 rounded-xl text-sm font-mono leading-relaxed text-slate-200 focus:outline-none resize-y"
          placeholder="Type markdown notes here..."
        />
      )}

      <div className="flex justify-between items-center text-xs text-slate-500 pt-2 border-t border-slate-800">
        <div className="flex gap-4">
          <span>Words: <strong className="text-slate-300">{wordCount}</strong></span>
          <span>Chars: <strong className="text-slate-300">{charCount}</strong></span>
        </div>
        <span>Last modified: {new Date(doc.updatedAt).toLocaleTimeString()}</span>
      </div>
    </div>
  );
};

export default NotesEditor;
