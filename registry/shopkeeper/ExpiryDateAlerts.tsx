import React, { useState, useMemo } from 'react';

/**
 * @name ExpiryDateAlerts
 * @domain shopkeeper
 * @description Perishable inventory and batch expiration tracking board with color-coded shelf-life alerts, clearance discount triggers, and wastage prevention.
 * @capability expiry-alerts, perishable-stock, batch-tracking, clearance-discount, wastage-prevention
 * @author Nexus Seed Registry Team
 */

export interface BatchItem {
  id: string;
  itemName: string;
  batchNumber: string;
  quantity: number;
  expiryDate: string; // YYYY-MM-DD
  originalPrice: number;
  discountPercentage: number;
}

export interface ExpiryDateAlertsProps {
  initialBatches?: BatchItem[];
  onApplyClearanceDiscount?: (item: BatchItem, discount: number) => void;
  className?: string;
}

const DEFAULT_BATCHES: BatchItem[] = [
  { id: 'b-1', itemName: 'Fresh Whole Milk 1L', batchNumber: 'MK-2026-09A', quantity: 18, expiryDate: '2026-09-29', originalPrice: 65, discountPercentage: 0 },
  { id: 'b-2', itemName: 'Greek Yogurt 400g', batchNumber: 'YG-2026-08B', quantity: 9, expiryDate: '2026-10-02', originalPrice: 120, discountPercentage: 20 },
  { id: 'b-3', itemName: 'Multigrain Bread 400g', batchNumber: 'BR-2026-09C', quantity: 12, expiryDate: '2026-09-28', originalPrice: 45, discountPercentage: 30 },
  { id: 'b-4', itemName: 'Salted Butter 200g', batchNumber: 'BT-2026-06X', quantity: 15, expiryDate: '2026-10-25', originalPrice: 115, discountPercentage: 0 },
  { id: 'b-5', itemName: 'Paneer Fresh 200g', batchNumber: 'PN-2026-09D', quantity: 6, expiryDate: '2026-09-27', originalPrice: 90, discountPercentage: 40 },
];

export const ExpiryDateAlerts: React.FC<ExpiryDateAlertsProps> = ({
  initialBatches = DEFAULT_BATCHES,
  onApplyClearanceDiscount,
  className = '',
}) => {
  const [batches, setBatches] = useState<BatchItem[]>(initialBatches);

  // Compute days remaining relative to today (assumed 2026-09-27)
  const evaluatedBatches = useMemo(() => {
    const today = new Date('2026-09-27');

    return batches.map((b) => {
      const exp = new Date(b.expiryDate);
      const diffTime = exp.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      let urgency: 'EXPIRED' | 'CRITICAL' | 'WARNING' | 'SAFE' = 'SAFE';
      if (diffDays < 0) urgency = 'EXPIRED';
      else if (diffDays <= 3) urgency = 'CRITICAL';
      else if (diffDays <= 14) urgency = 'WARNING';

      const effectivePrice = b.originalPrice * (1 - b.discountPercentage / 100);

      return {
        ...b,
        diffDays,
        urgency,
        effectivePrice: Number(effectivePrice.toFixed(2)),
      };
    });
  }, [batches]);

  const updateDiscount = (id: string, discount: number) => {
    setBatches((prev) =>
      prev.map((b) => {
        if (b.id === id) {
          const updated = { ...b, discountPercentage: discount };
          if (onApplyClearanceDiscount) onApplyClearanceDiscount(updated, discount);
          return updated;
        }
        return b;
      })
    );
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-red-400">Perishable Stock & Expiry Board</h2>
          <p className="text-xs text-slate-400">Prevent spoilage with proactive clearance discounts and shelf monitoring</p>
        </div>
        <span className="text-xs px-2.5 py-1 bg-red-950/70 text-red-300 border border-red-800/60 rounded-full font-semibold">
          Live Expiry Monitor
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {evaluatedBatches.map((b) => (
          <div
            key={b.id}
            className={`p-4 rounded-xl border transition-all ${
              b.urgency === 'EXPIRED'
                ? 'bg-rose-950/40 border-rose-800'
                : b.urgency === 'CRITICAL'
                ? 'bg-orange-950/30 border-orange-800/80'
                : b.urgency === 'WARNING'
                ? 'bg-amber-950/20 border-amber-800/50'
                : 'bg-slate-950/60 border-slate-800'
            }`}
          >
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-semibold text-slate-200">{b.itemName}</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                    {b.batchNumber}
                  </span>
                </div>
                <div className="flex gap-4 text-xs text-slate-400 mt-1">
                  <span>Expires: <strong className="text-slate-200">{b.expiryDate}</strong></span>
                  <span>Qty: <strong className="text-slate-200">{b.quantity} units</strong></span>
                </div>
              </div>

              <div className="text-right">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                  b.urgency === 'EXPIRED'
                    ? 'bg-rose-600 text-white'
                    : b.urgency === 'CRITICAL'
                    ? 'bg-orange-600 text-white'
                    : b.urgency === 'WARNING'
                    ? 'bg-amber-600 text-white'
                    : 'bg-emerald-800 text-emerald-200'
                }`}>
                  {b.diffDays < 0 ? 'EXPIRED' : b.diffDays === 0 ? 'EXPIRES TODAY' : `${b.diffDays} DAYS LEFT`}
                </span>
                <div className="mt-1 font-mono">
                  {b.discountPercentage > 0 ? (
                    <span className="text-xs">
                      <span className="line-through text-slate-500 mr-1.5">₹{b.originalPrice}</span>
                      <span className="font-bold text-emerald-400">₹{b.effectivePrice}</span>
                    </span>
                  ) : (
                    <span className="text-xs font-bold text-slate-300">₹{b.originalPrice}</span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-800/80 text-xs">
              <span className="text-slate-400">Clearance Discount:</span>
              <div className="flex gap-1.5">
                {[0, 15, 30, 50].map((pct) => (
                  <button
                    key={pct}
                    onClick={() => updateDiscount(b.id, pct)}
                    className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                      b.discountPercentage === pct
                        ? 'bg-orange-600 text-white'
                        : 'bg-slate-800 hover:bg-slate-700 text-slate-400'
                    }`}
                  >
                    {pct === 0 ? 'None' : `${pct}% off`}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExpiryDateAlerts;
