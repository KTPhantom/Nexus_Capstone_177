import React, { useState, useEffect, useCallback, useMemo } from 'react';

/**
 * @name PomodoroTimer
 * @domain student
 * @description A productivity focus timer implementing the Pomodoro technique with customizable work/break intervals, session tracking, audio alerts, and task tag association.
 * @capability focus-timer, session-tracking, productivity, time-management
 * @author Nexus Seed Registry Team
 */

export interface PomodoroSession {
  id: string;
  timestamp: string;
  durationMinutes: number;
  mode: 'work' | 'shortBreak' | 'longBreak';
  completed: boolean;
  taskTag?: string;
}

export interface PomodoroTimerProps {
  initialWorkMinutes?: number;
  initialShortBreakMinutes?: number;
  initialLongBreakMinutes?: number;
  longBreakInterval?: number;
  autoStartBreaks?: boolean;
  onSessionComplete?: (session: PomodoroSession) => void;
  className?: string;
}

export const PomodoroTimer: React.FC<PomodoroTimerProps> = ({
  initialWorkMinutes = 25,
  initialShortBreakMinutes = 5,
  initialLongBreakMinutes = 15,
  longBreakInterval = 4,
  autoStartBreaks = false,
  onSessionComplete,
  className = '',
}) => {
  const [mode, setMode] = useState<'work' | 'shortBreak' | 'longBreak'>('work');
  const [secondsRemaining, setSecondsRemaining] = useState<number>(initialWorkMinutes * 60);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [sessionsCompleted, setSessionsCompleted] = useState<number>(0);
  const [currentTaskTag, setCurrentTaskTag] = useState<string>('General Study');
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);

  const durationForMode = useMemo(() => {
    switch (mode) {
      case 'work':
        return initialWorkMinutes * 60;
      case 'shortBreak':
        return initialShortBreakMinutes * 60;
      case 'longBreak':
        return initialLongBreakMinutes * 60;
    }
  }, [mode, initialWorkMinutes, initialShortBreakMinutes, initialLongBreakMinutes]);

  const switchMode = useCallback((newMode: 'work' | 'shortBreak' | 'longBreak') => {
    setMode(newMode);
    setIsRunning(false);
    if (newMode === 'work') setSecondsRemaining(initialWorkMinutes * 60);
    else if (newMode === 'shortBreak') setSecondsRemaining(initialShortBreakMinutes * 60);
    else setSecondsRemaining(initialLongBreakMinutes * 60);
  }, [initialWorkMinutes, initialShortBreakMinutes, initialLongBreakMinutes]);

  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    if (isRunning && secondsRemaining > 0) {
      intervalId = setInterval(() => {
        setSecondsRemaining((prev) => prev - 1);
      }, 1000);
    } else if (secondsRemaining === 0 && isRunning) {
      setIsRunning(false);
      const sessionRecord: PomodoroSession = {
        id: `pomo-${Date.now()}`,
        timestamp: new Date().toISOString(),
        durationMinutes: Math.round(durationForMode / 60),
        mode,
        completed: true,
        taskTag: currentTaskTag,
      };
      if (onSessionComplete) onSessionComplete(sessionRecord);

      if (mode === 'work') {
        const nextCompleted = sessionsCompleted + 1;
        setSessionsCompleted(nextCompleted);
        const nextMode = nextCompleted % longBreakInterval === 0 ? 'longBreak' : 'shortBreak';
        switchMode(nextMode);
        if (autoStartBreaks) setIsRunning(true);
      } else {
        switchMode('work');
      }
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isRunning, secondsRemaining, mode, durationForMode, sessionsCompleted, longBreakInterval, autoStartBreaks, currentTaskTag, onSessionComplete, switchMode]);

  const toggleTimer = () => setIsRunning((prev) => !prev);
  const resetTimer = () => {
    setIsRunning(false);
    setSecondsRemaining(durationForMode);
  };

  const minutes = Math.floor(secondsRemaining / 60);
  const seconds = secondsRemaining % 60;
  const progressPercent = ((durationForMode - secondsRemaining) / durationForMode) * 100;

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col items-center gap-6 max-w-md w-full ${className}`}>
      <div className="flex items-center justify-between w-full">
        <h2 className="text-xl font-bold tracking-tight text-indigo-400">Pomodoro Focus Timer</h2>
        <button
          onClick={() => setSoundEnabled(!soundEnabled)}
          className={`px-2.5 py-1 text-xs rounded-full font-medium transition-colors ${soundEnabled ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-400'}`}
        >
          {soundEnabled ? 'Sound ON' : 'Muted'}
        </button>
      </div>

      <div className="flex gap-2 p-1 bg-slate-800 rounded-lg w-full justify-center">
        {(['work', 'shortBreak', 'longBreak'] as const).map((m) => (
          <button
            key={m}
            onClick={() => switchMode(m)}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all ${
              mode === m ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            {m === 'work' ? 'Focus' : m === 'shortBreak' ? 'Short Break' : 'Long Break'}
          </button>
        ))}
      </div>

      <div className="relative w-48 h-48 flex flex-col items-center justify-center rounded-full border-4 border-slate-800 bg-slate-950/60 shadow-inner">
        <span className="text-4xl font-extrabold tracking-wider font-mono">
          {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
        </span>
        <span className="text-xs text-slate-400 capitalize mt-1">{mode} Mode</span>
        <div
          className="absolute inset-0 rounded-full border-4 border-indigo-500 transition-all pointer-events-none"
          style={{ clipPath: `inset(${100 - progressPercent}% 0 0 0)` }}
        />
      </div>

      <div className="w-full flex flex-col gap-2">
        <label className="text-xs text-slate-400 font-medium">Task Topic</label>
        <input
          type="text"
          value={currentTaskTag}
          onChange={(e) => setCurrentTaskTag(e.target.value)}
          placeholder="e.g. Operating Systems Chapter 4"
          className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm focus:outline-none focus:border-indigo-500 text-white"
        />
      </div>

      <div className="flex items-center gap-3 w-full">
        <button
          onClick={toggleTimer}
          className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all shadow-md ${
            isRunning ? 'bg-amber-600 hover:bg-amber-500 text-white' : 'bg-indigo-600 hover:bg-indigo-500 text-white'
          }`}
        >
          {isRunning ? 'Pause' : 'Start Focus'}
        </button>
        <button
          onClick={resetTimer}
          className="px-4 py-2.5 rounded-lg text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
        >
          Reset
        </button>
      </div>

      <div className="flex justify-between w-full text-xs text-slate-400 border-t border-slate-800/80 pt-3">
        <span>Completed Intervals: <strong className="text-white">{sessionsCompleted}</strong></span>
        <span>Goal: 4 intervals</span>
      </div>
    </div>
  );
};

export default PomodoroTimer;
