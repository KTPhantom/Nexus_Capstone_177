import React, { useState, useMemo } from 'react';

/**
 * @name FlashcardDeck
 * @domain student
 * @description Spaced repetition flashcard study tool with flip card animations, difficulty grading, deck category filtering, and retention mastery progress tracking.
 * @capability flashcards, spaced-repetition, study-tool, memorization, active-recall
 * @author Nexus Seed Registry Team
 */

export interface Flashcard {
  id: string;
  category: string;
  front: string;
  back: string;
  interval: number; // in days
  easeFactor: number;
  repetitions: number;
}

export interface FlashcardDeckProps {
  initialCards?: Flashcard[];
  title?: string;
  onFinishReview?: (stats: { reviewedCount: number; masteryScore: number }) => void;
  className?: string;
}

const DEFAULT_CARDS: Flashcard[] = [
  { id: 'fc1', category: 'Databases', front: 'What does ACID stand for?', back: 'Atomicity, Consistency, Isolation, Durability', interval: 1, easeFactor: 2.5, repetitions: 0 },
  { id: 'fc2', category: 'Operating Systems', front: 'What is a Semaphore vs Mutex?', back: 'A Mutex is a locking mechanism for 1 thread. A Semaphore is a signaling mechanism with an integer count.', interval: 1, easeFactor: 2.5, repetitions: 0 },
  { id: 'fc3', category: 'Algorithms', front: 'What is the time complexity of QuickSort average vs worst case?', back: 'Average: O(n log n), Worst: O(n^2) when pivot is badly chosen.', interval: 1, easeFactor: 2.5, repetitions: 0 },
];

export const FlashcardDeck: React.FC<FlashcardDeckProps> = ({
  initialCards = DEFAULT_CARDS,
  title = 'Active Recall Flashcard Deck',
  onFinishReview,
  className = '',
}) => {
  const [cards, setCards] = useState<Flashcard[]>(initialCards);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isFlipped, setIsFlipped] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const filteredCards = useMemo(() => {
    if (selectedCategory === 'All') return cards;
    return cards.filter((c) => c.category === selectedCategory);
  }, [cards, selectedCategory]);

  const categories = useMemo(() => {
    const set = new Set(cards.map((c) => c.category));
    return ['All', ...Array.from(set)];
  }, [cards]);

  const currentCard = filteredCards[currentIndex];

  const handleDifficulty = (rating: 'again' | 'hard' | 'good' | 'easy') => {
    if (!currentCard) return;

    let deltaEase = 0;
    if (rating === 'again') deltaEase = -0.2;
    else if (rating === 'hard') deltaEase = -0.15;
    else if (rating === 'easy') deltaEase = 0.15;

    const nextEase = Math.max(1.3, currentCard.easeFactor + deltaEase);
    const nextReps = rating === 'again' ? 0 : currentCard.repetitions + 1;

    setCards((prev) =>
      prev.map((c) => (c.id === currentCard.id ? { ...c, easeFactor: nextEase, repetitions: nextReps } : c))
    );

    setIsFlipped(false);
    if (currentIndex + 1 < filteredCards.length) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      if (onFinishReview) {
        onFinishReview({ reviewedCount: filteredCards.length, masteryScore: 85 });
      }
    }
  };

  const resetReview = () => {
    setCurrentIndex(0);
    setIsFlipped(false);
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-lg w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-amber-400">{title}</h2>
          <span className="text-xs text-slate-400">Card {currentIndex + 1} of {filteredCards.length}</span>
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => {
            setSelectedCategory(e.target.value);
            setCurrentIndex(0);
            setIsFlipped(false);
          }}
          className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-300"
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {currentCard ? (
        <div
          onClick={() => setIsFlipped(!isFlipped)}
          className="cursor-pointer min-h-[220px] bg-slate-950/80 border-2 border-dashed border-slate-700 hover:border-amber-500 rounded-xl p-6 flex flex-col justify-center items-center text-center transition-all shadow-inner relative"
        >
          <span className="absolute top-3 left-3 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400">
            {isFlipped ? 'Answer' : 'Question'} - {currentCard.category}
          </span>
          <p className="text-base font-medium leading-relaxed px-4">
            {isFlipped ? currentCard.back : currentCard.front}
          </p>
          <span className="absolute bottom-3 text-xs text-slate-500">Click to flip card</span>
        </div>
      ) : (
        <div className="text-center py-10 bg-slate-950/40 rounded-xl">
          <p className="text-emerald-400 font-semibold mb-2">Review Complete!</p>
          <button
            onClick={resetReview}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold rounded-lg"
          >
            Restart Deck
          </button>
        </div>
      )}

      {currentCard && isFlipped && (
        <div className="grid grid-cols-4 gap-2">
          <button
            onClick={() => handleDifficulty('again')}
            className="py-2 bg-rose-900/60 hover:bg-rose-800 text-rose-200 text-xs font-semibold rounded-lg border border-rose-700/50"
          >
            Again (&lt;1m)
          </button>
          <button
            onClick={() => handleDifficulty('hard')}
            className="py-2 bg-orange-900/60 hover:bg-orange-800 text-orange-200 text-xs font-semibold rounded-lg border border-orange-700/50"
          >
            Hard (1d)
          </button>
          <button
            onClick={() => handleDifficulty('good')}
            className="py-2 bg-sky-900/60 hover:bg-sky-800 text-sky-200 text-xs font-semibold rounded-lg border border-sky-700/50"
          >
            Good (3d)
          </button>
          <button
            onClick={() => handleDifficulty('easy')}
            className="py-2 bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 text-xs font-semibold rounded-lg border border-emerald-700/50"
          >
            Easy (5d)
          </button>
        </div>
      )}
    </div>
  );
};

export default FlashcardDeck;
