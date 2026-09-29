import React, { useState, useMemo } from 'react';

/**
 * @name AssignmentTracker
 * @domain student
 * @description Academic deadline and homework tracker supporting course filtering, due date countdown, urgency indicators, and submission status management.
 * @capability assignment-tracking, deadline-alerts, homework-management, course-tasks
 * @author Nexus Seed Registry Team
 */

export interface Assignment {
  id: string;
  title: string;
  course: string;
  dueDate: string; // YYYY-MM-DD
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'submitted';
  weightPercentage?: number;
}

export interface AssignmentTrackerProps {
  initialAssignments?: Assignment[];
  onAssignmentComplete?: (assignment: Assignment) => void;
  className?: string;
}

const DEFAULT_ASSIGNMENTS: Assignment[] = [
  { id: 'a1', title: 'Raft Consensus Implementation', course: 'CS301', dueDate: '2026-10-05', priority: 'high', status: 'in_progress', weightPercentage: 20 },
  { id: 'a2', title: 'Lexical Analyzer AST Lab', course: 'CS302', dueDate: '2026-10-02', priority: 'high', status: 'pending', weightPercentage: 15 },
  { id: 'a3', title: 'TCP Congestion Control Report', course: 'CS303', dueDate: '2026-10-12', priority: 'medium', status: 'pending', weightPercentage: 10 },
];

export const AssignmentTracker: React.FC<AssignmentTrackerProps> = ({
  initialAssignments = DEFAULT_ASSIGNMENTS,
  onAssignmentComplete,
  className = '',
}) => {
  const [assignments, setAssignments] = useState<Assignment[]>(initialAssignments);
  const [filterCourse, setFilterCourse] = useState<string>('All');
  const [filterStatus, setFilterStatus] = useState<string>('All');

  const [title, setTitle] = useState('');
  const [course, setCourse] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState<Assignment['priority']>('medium');

  const courses = useMemo(() => {
    return ['All', ...Array.from(new Set(assignments.map((a) => a.course)))];
  }, [assignments]);

  const filtered = useMemo(() => {
    return assignments.filter((a) => {
      const matchCourse = filterCourse === 'All' || a.course === filterCourse;
      const matchStatus = filterStatus === 'All' || a.status === filterStatus;
      return matchCourse && matchStatus;
    });
  }, [assignments, filterCourse, filterStatus]);

  const addAssignment = () => {
    if (!title.trim() || !course.trim() || !dueDate) return;
    const item: Assignment = {
      id: `asg-${Date.now()}`,
      title,
      course: course.toUpperCase(),
      dueDate,
      priority,
      status: 'pending',
    };
    setAssignments([...assignments, item]);
    setTitle('');
    setCourse('');
    setDueDate('');
  };

  const toggleStatus = (id: string) => {
    const updated = assignments.map((a) => {
      if (a.id === id) {
        const nextStatus: Assignment['status'] =
          a.status === 'pending' ? 'in_progress' : a.status === 'in_progress' ? 'submitted' : 'pending';
        const updatedItem = { ...a, status: nextStatus };
        if (nextStatus === 'submitted' && onAssignmentComplete) {
          onAssignmentComplete(updatedItem);
        }
        return updatedItem;
      }
      return a;
    });
    setAssignments(updated);
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Assignment & Due Date Tracker</h2>
          <p className="text-xs text-slate-400">Stay ahead of academic deadlines and project deliverables</p>
        </div>
        <div className="flex gap-2">
          <select
            value={filterCourse}
            onChange={(e) => setFilterCourse(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-xs px-2.5 py-1 rounded-lg text-slate-300"
          >
            {courses.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-xs px-2.5 py-1 rounded-lg text-slate-300"
          >
            <option value="All">All Status</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="submitted">Submitted</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 bg-slate-800/80 p-3 rounded-xl border border-slate-700">
        <input
          type="text"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
        />
        <input
          type="text"
          placeholder="Course"
          value={course}
          onChange={(e) => setCourse(e.target.value)}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
        />
        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
        />
        <div className="flex gap-1">
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as Assignment['priority'])}
            className="flex-1 px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
          >
            <option value="low">Low</option>
            <option value="medium">Med</option>
            <option value="high">High</option>
          </select>
          <button
            onClick={addAssignment}
            className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 rounded text-xs font-semibold text-white"
          >
            Add
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {filtered.map((a) => (
          <div
            key={a.id}
            onClick={() => toggleStatus(a.id)}
            className="flex items-center justify-between p-3 bg-slate-950/60 border border-slate-800 hover:border-slate-700 rounded-xl cursor-pointer transition-all"
          >
            <div className="flex items-center gap-3">
              <span className={`w-2.5 h-2.5 rounded-full ${
                a.status === 'submitted' ? 'bg-emerald-500' : a.status === 'in_progress' ? 'bg-amber-500' : 'bg-slate-600'
              }`} />
              <div>
                <p className={`text-sm font-medium ${a.status === 'submitted' ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                  {a.title}
                </p>
                <div className="flex gap-2 text-xs text-slate-400 mt-0.5">
                  <span className="font-mono text-cyan-400">{a.course}</span>
                  <span>•</span>
                  <span>Due: {a.dueDate}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                a.priority === 'high' ? 'bg-rose-900/60 text-rose-300' : a.priority === 'medium' ? 'bg-amber-900/60 text-amber-300' : 'bg-slate-800 text-slate-400'
              }`}>
                {a.priority}
              </span>
              <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 capitalize font-medium">
                {a.status.replace('_', ' ')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AssignmentTracker;
