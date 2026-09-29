import React, { useState, useMemo } from 'react';

/**
 * @name AttendanceTracker
 * @domain student
 * @description College course attendance threshold monitor calculating percentage, bunk allowance, and mandatory classes needed to sustain 75% or 80% criteria.
 * @capability attendance-tracker, bunk-calculator, lecture-log, minimum-threshold
 * @author Nexus Seed Registry Team
 */

export interface SubjectAttendance {
  id: string;
  courseCode: string;
  courseName: string;
  attended: number;
  totalHeld: number;
}

export interface AttendanceTrackerProps {
  initialSubjects?: SubjectAttendance[];
  targetPercentage?: number;
  onAttendanceAlert?: (subject: SubjectAttendance, isLow: boolean) => void;
  className?: string;
}

const DEFAULT_SUBJECTS: SubjectAttendance[] = [
  { id: 's1', courseCode: 'CS301', courseName: 'Distributed Systems', attended: 24, totalHeld: 28 },
  { id: 's2', courseCode: 'CS302', courseName: 'Compiler Design', attended: 19, totalHeld: 26 },
  { id: 's3', courseCode: 'CS303', courseName: 'Computer Networks', attended: 22, totalHeld: 24 },
];

export const AttendanceTracker: React.FC<AttendanceTrackerProps> = ({
  initialSubjects = DEFAULT_SUBJECTS,
  targetPercentage = 75,
  onAttendanceAlert,
  className = '',
}) => {
  const [subjects, setSubjects] = useState<SubjectAttendance[]>(initialSubjects);

  const stats = useMemo(() => {
    return subjects.map((sub) => {
      const percentage = sub.totalHeld > 0 ? (sub.attended / sub.totalHeld) * 100 : 100;
      const isShort = percentage < targetPercentage;

      // Safe bunks calculation: (attended / (totalHeld + x)) >= target / 100
      // x <= (attended * 100 / target) - totalHeld
      const targetRatio = targetPercentage / 100;
      let safeBunks = 0;
      let neededToCatchUp = 0;

      if (!isShort) {
        safeBunks = Math.floor(sub.attended / targetRatio - sub.totalHeld);
      } else {
        // (attended + y) / (totalHeld + y) >= target / 100
        // y * (1 - targetRatio) >= targetRatio * totalHeld - attended
        neededToCatchUp = Math.ceil((targetRatio * sub.totalHeld - sub.attended) / (1 - targetRatio));
      }

      return {
        ...sub,
        percentage: Number(percentage.toFixed(1)),
        isShort,
        safeBunks: Math.max(0, safeBunks),
        neededToCatchUp: Math.max(0, neededToCatchUp),
      };
    });
  }, [subjects, targetPercentage]);

  const markAttendance = (id: string, attendedDelta: number, heldDelta: number) => {
    setSubjects((prev) =>
      prev.map((sub) => {
        if (sub.id === id) {
          const nextAttended = Math.max(0, sub.attended + attendedDelta);
          const nextHeld = Math.max(nextAttended, sub.totalHeld + heldDelta);
          const updated = { ...sub, attended: nextAttended, totalHeld: nextHeld };
          const pct = nextHeld > 0 ? (nextAttended / nextHeld) * 100 : 100;
          if (onAttendanceAlert) onAttendanceAlert(updated, pct < targetPercentage);
          return updated;
        }
        return sub;
      })
    );
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-teal-400">Class Attendance & Bunk Monitor</h2>
          <p className="text-xs text-slate-400">Stay above the {targetPercentage}% university criteria</p>
        </div>
        <span className="text-xs px-2.5 py-1 bg-teal-950/70 text-teal-300 border border-teal-800/60 rounded-full font-semibold">
          Threshold: {targetPercentage}%
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {stats.map((item) => (
          <div
            key={item.id}
            className={`p-4 rounded-xl border transition-all ${
              item.isShort
                ? 'bg-rose-950/20 border-rose-800/60'
                : 'bg-slate-950/60 border-slate-800 hover:border-teal-500/40'
            }`}
          >
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono text-xs text-teal-400 font-bold">{item.courseCode}</span>
                <h4 className="text-sm font-semibold text-slate-200">{item.courseName}</h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Attended: {item.attended} / {item.totalHeld} lectures
                </p>
              </div>
              <div className="text-right">
                <span className={`text-2xl font-extrabold ${item.isShort ? 'text-rose-400' : 'text-teal-400'}`}>
                  {item.percentage}%
                </span>
                <div className="text-[11px] font-medium mt-0.5">
                  {item.isShort ? (
                    <span className="text-rose-400">Attend next {item.neededToCatchUp} classes</span>
                  ) : (
                    <span className="text-emerald-400">Can skip {item.safeBunks} classes</span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-2 mt-3 pt-3 border-t border-slate-800/80 justify-end">
              <button
                onClick={() => markAttendance(item.id, 1, 1)}
                className="px-3 py-1 bg-teal-600 hover:bg-teal-500 text-xs font-semibold rounded text-white shadow-sm"
              >
                + Present
              </button>
              <button
                onClick={() => markAttendance(item.id, 0, 1)}
                className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-xs font-semibold rounded text-white shadow-sm"
              >
                + Absent
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AttendanceTracker;
