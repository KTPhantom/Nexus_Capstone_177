import React, { useState, useMemo } from 'react';

/**
 * @name GradeTracker
 * @domain student
 * @description Academic grade and GPA calculator enabling students to record course grades, credit weights, calculate SGPA and cumulative CGPA, and project target grades.
 * @capability gpa-calculation, cgpa, sgpa, grade-tracking, academic-records
 * @author Nexus Seed Registry Team
 */

export interface CourseGrade {
  id: string;
  courseCode: string;
  courseName: string;
  credits: number;
  letterGrade: 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D' | 'F';
  gradePoints?: number;
}

export interface GradeTrackerProps {
  initialCourses?: CourseGrade[];
  scale?: '4.0' | '10.0';
  targetGpa?: number;
  onGradeUpdate?: (courses: CourseGrade[], currentGpa: number) => void;
  className?: string;
}

const GRADE_POINTS_10: Record<CourseGrade['letterGrade'], number> = {
  'A+': 10,
  'A': 9,
  'B+': 8,
  'B': 7,
  'C+': 6,
  'C': 5,
  'D': 4,
  'F': 0,
};

const GRADE_POINTS_4: Record<CourseGrade['letterGrade'], number> = {
  'A+': 4.0,
  'A': 3.7,
  'B+': 3.3,
  'B': 3.0,
  'C+': 2.3,
  'C': 2.0,
  'D': 1.0,
  'F': 0.0,
};

export const GradeTracker: React.FC<GradeTrackerProps> = ({
  initialCourses = [
    { id: 'c1', courseCode: 'CS301', courseName: 'Distributed Systems', credits: 4, letterGrade: 'A' },
    { id: 'c2', courseCode: 'CS302', courseName: 'Compiler Design', credits: 4, letterGrade: 'B+' },
    { id: 'c3', courseCode: 'CS303', courseName: 'Computer Networks', credits: 3, letterGrade: 'A+' },
  ],
  scale = '10.0',
  targetGpa = 9.0,
  onGradeUpdate,
  className = '',
}) => {
  const [courses, setCourses] = useState<CourseGrade[]>(initialCourses);
  const [newCode, setNewCode] = useState<string>('');
  const [newName, setNewName] = useState<string>('');
  const [newCredits, setNewCredits] = useState<number>(3);
  const [newGrade, setNewGrade] = useState<CourseGrade['letterGrade']>('A');

  const gradeTable = scale === '10.0' ? GRADE_POINTS_10 : GRADE_POINTS_4;

  const { totalCredits, gpa } = useMemo(() => {
    let earnedPoints = 0;
    let creditsSum = 0;

    courses.forEach((c) => {
      const pts = gradeTable[c.letterGrade] ?? 0;
      earnedPoints += pts * c.credits;
      creditsSum += c.credits;
    });

    const calculated = creditsSum > 0 ? earnedPoints / creditsSum : 0;
    return {
      totalCredits: creditsSum,
      gpa: Number(calculated.toFixed(2)),
    };
  }, [courses, gradeTable]);

  const addCourse = () => {
    if (!newCode.trim() || !newName.trim()) return;
    const item: CourseGrade = {
      id: `crs-${Date.now()}`,
      courseCode: newCode.toUpperCase(),
      courseName: newName,
      credits: Number(newCredits),
      letterGrade: newGrade,
      gradePoints: gradeTable[newGrade],
    };
    const updated = [...courses, item];
    setCourses(updated);
    setNewCode('');
    setNewName('');
    if (onGradeUpdate) onGradeUpdate(updated, gpa);
  };

  const removeCourse = (id: string) => {
    const updated = courses.filter((c) => c.id !== id);
    setCourses(updated);
    if (onGradeUpdate) onGradeUpdate(updated, gpa);
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Academic Grade & GPA Tracker</h2>
          <p className="text-xs text-slate-400">Track semester performance, weighted credits, and target honors</p>
        </div>
        <div className="text-right">
          <span className="text-xs uppercase tracking-wide text-slate-400">Current GPA</span>
          <div className="text-3xl font-extrabold text-emerald-400">{gpa} / {scale}</div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 bg-slate-800 p-3 rounded-xl border border-slate-700">
        <input
          type="text"
          placeholder="Course Code"
          value={newCode}
          onChange={(e) => setNewCode(e.target.value)}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-white"
        />
        <input
          type="text"
          placeholder="Course Title"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-white"
        />
        <input
          type="number"
          min="1"
          max="8"
          value={newCredits}
          onChange={(e) => setNewCredits(Number(e.target.value))}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-white"
        />
        <div className="flex gap-2">
          <select
            value={newGrade}
            onChange={(e) => setNewGrade(e.target.value as CourseGrade['letterGrade'])}
            className="flex-1 px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-white"
          >
            {Object.keys(gradeTable).map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
          <button
            onClick={addCourse}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 rounded text-sm font-semibold text-white shadow-sm"
          >
            Add
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
              <th className="py-2 px-3">Code</th>
              <th className="py-2 px-3">Course</th>
              <th className="py-2 px-3">Credits</th>
              <th className="py-2 px-3">Grade</th>
              <th className="py-2 px-3">Points</th>
              <th className="py-2 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {courses.map((c) => (
              <tr key={c.id} className="hover:bg-slate-800/40">
                <td className="py-2 px-3 font-mono font-medium text-emerald-300">{c.courseCode}</td>
                <td className="py-2 px-3">{c.courseName}</td>
                <td className="py-2 px-3">{c.credits}</td>
                <td className="py-2 px-3 font-semibold">{c.letterGrade}</td>
                <td className="py-2 px-3 text-slate-400">{gradeTable[c.letterGrade] * c.credits}</td>
                <td className="py-2 px-3 text-right">
                  <button
                    onClick={() => removeCourse(c.id)}
                    className="text-xs text-rose-400 hover:text-rose-300"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center text-xs text-slate-400 pt-2 border-t border-slate-800">
        <span>Total Credits Earned: <strong className="text-white">{totalCredits}</strong></span>
        <span>Target GPA: <strong className={gpa >= targetGpa ? 'text-emerald-400' : 'text-amber-400'}>{targetGpa}</strong></span>
      </div>
    </div>
  );
};

export default GradeTracker;
