import React, { useState, useMemo } from 'react';

/**
 * @name DailyCashLedger
 * @domain shopkeeper
 * @description Small business cashbook and daily transaction ledger tracking cash, UPI, and card payments with running balance and opening/closing cash tally.
 * @capability cash-ledger, daily-accounts, upi-tracking, cashflow, retail-accounting
 * @author Nexus Seed Registry Team
 */

export type PaymentMethod = 'CASH' | 'UPI' | 'CARD';
export type TransactionType = 'IN' | 'OUT';

export interface LedgerEntry {
  id: string;
  timestamp: string;
  type: TransactionType;
  amount: number;
  paymentMethod: PaymentMethod;
  description: string;
}

export interface DailyCashLedgerProps {
  initialOpeningCash?: number;
  initialEntries?: LedgerEntry[];
  onTallyClose?: (closingBalance: number, entries: LedgerEntry[]) => void;
  className?: string;
}

const DEFAULT_ENTRIES: LedgerEntry[] = [
  { id: 'tx-1', timestamp: '09:15 AM', type: 'IN', amount: 450, paymentMethod: 'CASH', description: 'Grocery items sold' },
  { id: 'tx-2', timestamp: '10:30 AM', type: 'IN', amount: 1200, paymentMethod: 'UPI', description: 'Cooking oil & spices bulk' },
  { id: 'tx-3', timestamp: '11:45 AM', type: 'OUT', amount: 350, paymentMethod: 'CASH', description: 'Milk crate distributor delivery' },
  { id: 'tx-4', timestamp: '01:20 PM', type: 'IN', amount: 820, paymentMethod: 'UPI', description: 'Snacks & beverages' },
];

export const DailyCashLedger: React.FC<DailyCashLedgerProps> = ({
  initialOpeningCash = 5000,
  initialEntries = DEFAULT_ENTRIES,
  onTallyClose,
  className = '',
}) => {
  const [openingCash, setOpeningCash] = useState<number>(initialOpeningCash);
  const [entries, setEntries] = useState<LedgerEntry[]>(initialEntries);
  const [desc, setDesc] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [type, setType] = useState<TransactionType>('IN');
  const [method, setMethod] = useState<PaymentMethod>('CASH');

  const { totalIn, totalOut, netBalance, cashInHand } = useMemo(() => {
    let tin = 0;
    let tout = 0;
    let cashChange = 0;

    entries.forEach((e) => {
      if (e.type === 'IN') {
        tin += e.amount;
        if (e.paymentMethod === 'CASH') cashChange += e.amount;
      } else {
        tout += e.amount;
        if (e.paymentMethod === 'CASH') cashChange -= e.amount;
      }
    });

    return {
      totalIn: tin,
      totalOut: tout,
      netBalance: openingCash + tin - tout,
      cashInHand: openingCash + cashChange,
    };
  }, [entries, openingCash]);

  const addEntry = () => {
    const val = parseFloat(amount);
    if (isNaN(val) || val <= 0 || !desc.trim()) return;

    const newEntry: LedgerEntry = {
      id: `tx-${Date.now()}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      type,
      amount: val,
      paymentMethod: method,
      description: desc.trim(),
    };

    setEntries([newEntry, ...entries]);
    setDesc('');
    setAmount('');
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-amber-400">Daily Cash & UPI Ledger</h2>
          <p className="text-xs text-slate-400">Track counter cash, GooglePay/PhonePe UPI inflow and supplier payouts</p>
        </div>
        <div className="text-right">
          <span className="text-[10px] uppercase tracking-wider text-slate-400">Net Till Balance</span>
          <div className="text-2xl font-extrabold text-amber-400">₹{netBalance.toLocaleString()}</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
          <span className="text-xs text-emerald-400">Today's Inflow (Sales)</span>
          <div className="text-lg font-bold text-white mt-1">₹{totalIn.toLocaleString()}</div>
        </div>
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
          <span className="text-xs text-rose-400">Today's Outflow (Expense)</span>
          <div className="text-lg font-bold text-white mt-1">₹{totalOut.toLocaleString()}</div>
        </div>
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
          <span className="text-xs text-sky-400">Physical Cash in Drawer</span>
          <div className="text-lg font-bold text-white mt-1">₹{cashInHand.toLocaleString()}</div>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-2 bg-slate-800/80 p-3 rounded-xl border border-slate-700">
        <div className="flex rounded overflow-hidden">
          <button
            onClick={() => setType('IN')}
            className={`flex-1 text-xs font-bold py-1.5 ${type === 'IN' ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-slate-400'}`}
          >
            IN (+)
          </button>
          <button
            onClick={() => setType('OUT')}
            className={`flex-1 text-xs font-bold py-1.5 ${type === 'OUT' ? 'bg-rose-600 text-white' : 'bg-slate-900 text-slate-400'}`}
          >
            OUT (-)
          </button>
        </div>

        <input
          type="number"
          placeholder="₹ Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
        />

        <select
          value={method}
          onChange={(e) => setMethod(e.target.value as PaymentMethod)}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
        >
          <option value="CASH">Cash</option>
          <option value="UPI">UPI / QR</option>
          <option value="CARD">Card / POS</option>
        </select>

        <input
          type="text"
          placeholder="Reason / Customer / Supplier"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          className="px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
        />

        <button
          onClick={addEntry}
          className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 rounded text-xs font-semibold text-white shadow-sm"
        >
          Record
        </button>
      </div>

      <div className="overflow-x-auto max-h-[260px]">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase">
              <th className="py-2 px-3">Time</th>
              <th className="py-2 px-3">Type</th>
              <th className="py-2 px-3">Description</th>
              <th className="py-2 px-3">Mode</th>
              <th className="py-2 px-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {entries.map((e) => (
              <tr key={e.id} className="hover:bg-slate-800/40">
                <td className="py-2 px-3 text-slate-400 font-mono">{e.timestamp}</td>
                <td className="py-2 px-3">
                  <span className={`px-1.5 py-0.5 rounded font-bold text-[10px] ${e.type === 'IN' ? 'bg-emerald-950 text-emerald-300' : 'bg-rose-950 text-rose-300'}`}>
                    {e.type}
                  </span>
                </td>
                <td className="py-2 px-3 font-medium text-slate-200">{e.description}</td>
                <td className="py-2 px-3 text-slate-400">{e.paymentMethod}</td>
                <td className={`py-2 px-3 text-right font-bold font-mono ${e.type === 'IN' ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {e.type === 'IN' ? '+' : '-'}₹{e.amount}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DailyCashLedger;
