import React, { useState, useMemo } from 'react';

/**
 * @name ProfitMarginCalculator
 * @domain shopkeeper
 * @description Retail profit margin and pricing calculator analyzing cost price, selling price, GST tax rates, markup percentages, and net unit margins.
 * @capability margin-calculator, gst-pricing, markup-calculator, retail-profit, price-optimization
 * @author Nexus Seed Registry Team
 */

export interface PricingBreakdown {
  costPrice: number;
  sellingPrice: number;
  gstRate: number; // e.g. 5, 12, 18
  gstAmount: number;
  grossProfit: number;
  grossMarginPercentage: number;
  markupPercentage: number;
  netUnitProfit: number;
}

export interface ProfitMarginCalculatorProps {
  initialCost?: number;
  initialSellingPrice?: number;
  initialGstRate?: number;
  onCalculationChange?: (breakdown: PricingBreakdown) => void;
  className?: string;
}

export const ProfitMarginCalculator: React.FC<ProfitMarginCalculatorProps> = ({
  initialCost = 120,
  initialSellingPrice = 160,
  initialGstRate = 5,
  onCalculationChange,
  className = '',
}) => {
  const [costPrice, setCostPrice] = useState<number>(initialCost);
  const [sellingPrice, setSellingPrice] = useState<number>(initialSellingPrice);
  const [gstRate, setGstRate] = useState<number>(initialGstRate);
  const [overheadExpense, setOverheadExpense] = useState<number>(5);

  const breakdown: PricingBreakdown = useMemo(() => {
    // Selling price inclusive of GST
    const baseSellingPrice = sellingPrice / (1 + gstRate / 100);
    const gstAmount = sellingPrice - baseSellingPrice;
    const grossProfit = baseSellingPrice - costPrice;
    const grossMarginPercentage = baseSellingPrice > 0 ? (grossProfit / baseSellingPrice) * 100 : 0;
    const markupPercentage = costPrice > 0 ? ((baseSellingPrice - costPrice) / costPrice) * 100 : 0;
    const netUnitProfit = grossProfit - overheadExpense;

    const res: PricingBreakdown = {
      costPrice,
      sellingPrice,
      gstRate,
      gstAmount: Number(gstAmount.toFixed(2)),
      grossProfit: Number(grossProfit.toFixed(2)),
      grossMarginPercentage: Number(grossMarginPercentage.toFixed(1)),
      markupPercentage: Number(markupPercentage.toFixed(1)),
      netUnitProfit: Number(netUnitProfit.toFixed(2)),
    };

    if (onCalculationChange) onCalculationChange(res);
    return res;
  }, [costPrice, sellingPrice, gstRate, overheadExpense, onCalculationChange]);

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-lime-400">Retail Profit & Margin Calculator</h2>
          <p className="text-xs text-slate-400">Calculate net margins after GST, logistics, and wholesale discounts</p>
        </div>
        <div className="text-right">
          <span className="text-[10px] uppercase tracking-wider text-slate-400">Gross Margin</span>
          <div className={`text-2xl font-extrabold ${breakdown.grossMarginPercentage >= 15 ? 'text-lime-400' : 'text-amber-400'}`}>
            {breakdown.grossMarginPercentage}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 bg-slate-800/60 p-4 rounded-xl border border-slate-700">
        <div>
          <label className="text-xs text-slate-400 block mb-1">Wholesale Cost Price (₹)</label>
          <input
            type="number"
            value={costPrice}
            onChange={(e) => setCostPrice(Math.max(0, parseFloat(e.target.value) || 0))}
            className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white font-mono"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 block mb-1">Selling Price / MRP (₹)</label>
          <input
            type="number"
            value={sellingPrice}
            onChange={(e) => setSellingPrice(Math.max(0, parseFloat(e.target.value) || 0))}
            className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white font-mono"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 block mb-1">GST Tax Bracket</label>
          <select
            value={gstRate}
            onChange={(e) => setGstRate(Number(e.target.value))}
            className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white font-mono"
          >
            <option value="0">0% (Exempt)</option>
            <option value="5">5% (Essential food/items)</option>
            <option value="12">12% (Standard goods)</option>
            <option value="18">18% (Consumer goods)</option>
            <option value="28">28% (Luxury items)</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-slate-400 block mb-1">Est. Overhead / Packaging (₹)</label>
          <input
            type="number"
            value={overheadExpense}
            onChange={(e) => setOverheadExpense(Math.max(0, parseFloat(e.target.value) || 0))}
            className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white font-mono"
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">GST Output Tax</span>
          <div className="text-base font-bold text-slate-200 mt-1">₹{breakdown.gstAmount}</div>
        </div>
        <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Markup on Cost</span>
          <div className="text-base font-bold text-slate-200 mt-1">{breakdown.markupPercentage}%</div>
        </div>
        <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
          <span className="text-[10px] text-lime-400 uppercase tracking-wider font-semibold">Net Unit Profit</span>
          <div className={`text-base font-bold mt-1 ${breakdown.netUnitProfit >= 0 ? 'text-lime-400' : 'text-rose-400'}`}>
            ₹{breakdown.netUnitProfit}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfitMarginCalculator;
