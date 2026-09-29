import React, { useState, useMemo } from 'react';

/**
 * @name CustomerUdharKhata
 * @domain shopkeeper
 * @description Local retail customer credit ledger (Udhar Khata) tracking individual balances, credit limits, repayment installments, and WhatsApp payment reminder dispatch.
 * @capability credit-ledger, udhar-khata, customer-debt, payment-reminders, khata-book
 * @author Nexus Seed Registry Team
 */

export interface KhataCustomer {
  id: string;
  name: string;
  phone: string;
  currentDebt: number;
  creditLimit: number;
  lastPaymentDate: string;
}

export interface CustomerUdharKhataProps {
  initialCustomers?: KhataCustomer[];
  onSendReminder?: (customer: KhataCustomer) => void;
  className?: string;
}

const DEFAULT_CUSTOMERS: KhataCustomer[] = [
  { id: 'k-1', name: 'Ramesh Sharma', phone: '9823456789', currentDebt: 3450, creditLimit: 5000, lastPaymentDate: '2026-09-15' },
  { id: 'k-2', name: 'Dr. Sunita Verma', phone: '9876501234', currentDebt: 1200, creditLimit: 3000, lastPaymentDate: '2026-09-22' },
  { id: 'k-3', name: 'Anil Kumar (Pvt Ltd)', phone: '9911223344', currentDebt: 7800, creditLimit: 8000, lastPaymentDate: '2026-09-10' },
  { id: 'k-4', name: 'Pooja Tiwari', phone: '9788776655', currentDebt: 450, creditLimit: 2000, lastPaymentDate: '2026-09-26' },
];

export const CustomerUdharKhata: React.FC<CustomerUdharKhataProps> = ({
  initialCustomers = DEFAULT_CUSTOMERS,
  onSendReminder,
  className = '',
}) => {
  const [customers, setCustomers] = useState<KhataCustomer[]>(initialCustomers);
  const [search, setSearch] = useState<string>('');
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const [repayAmount, setRepayAmount] = useState<string>('');

  const totalOutstanding = useMemo(() => {
    return customers.reduce((sum, c) => sum + c.currentDebt, 0);
  }, [customers]);

  const filtered = useMemo(() => {
    return customers.filter(
      (c) =>
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        c.phone.includes(search)
    );
  }, [customers, search]);

  const recordPayment = (customerId: string) => {
    const val = parseFloat(repayAmount);
    if (isNaN(val) || val <= 0) return;

    setCustomers((prev) =>
      prev.map((c) => {
        if (c.id === customerId) {
          const nextDebt = Math.max(0, c.currentDebt - val);
          return {
            ...c,
            currentDebt: nextDebt,
            lastPaymentDate: new Date().toISOString().split('T')[0],
          };
        }
        return c;
      })
    );
    setRepayAmount('');
    setSelectedCustomerId(null);
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-amber-400">Customer Udhar & Credit Khata</h2>
          <p className="text-xs text-slate-400">Manage store credit, trusted customer tabs, and send WhatsApp balance alerts</p>
        </div>
        <div className="text-right">
          <span className="text-[10px] uppercase tracking-wider text-slate-400">Total Outstanding</span>
          <div className="text-2xl font-extrabold text-rose-400">₹{totalOutstanding.toLocaleString()}</div>
        </div>
      </div>

      <input
        type="text"
        placeholder="Search customer by name or phone..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-3 py-2 bg-slate-950/70 border border-slate-700 rounded-lg text-xs text-white"
      />

      <div className="flex flex-col gap-3">
        {filtered.map((c) => {
          const isNearLimit = c.currentDebt >= c.creditLimit * 0.9;
          return (
            <div
              key={c.id}
              className={`p-4 rounded-xl border transition-all ${
                isNearLimit ? 'bg-rose-950/20 border-rose-800/60' : 'bg-slate-950/60 border-slate-800'
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-slate-200">{c.name}</h4>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                      {c.phone}
                    </span>
                  </div>
                  <div className="flex gap-4 text-xs text-slate-400 mt-1">
                    <span>Credit Limit: <strong className="text-slate-300">₹{c.creditLimit}</strong></span>
                    <span>Last Paid: <strong className="text-slate-300">{c.lastPaymentDate}</strong></span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs text-slate-400 block">Pending Debt</span>
                  <span className="text-lg font-bold font-mono text-rose-400">₹{c.currentDebt.toLocaleString()}</span>
                </div>
              </div>

              <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-800/80">
                <a
                  href={`https://wa.me/91${c.phone}?text=Namaste%20${encodeURIComponent(c.name)},%20your%20pending%20balance%20at%20our%20store%20is%20Rs.${c.currentDebt}.%20Kindly%20clear%20at%20your%20earliest.`}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => onSendReminder && onSendReminder(c)}
                  className="px-3 py-1 bg-emerald-600/80 hover:bg-emerald-500 text-white rounded text-xs font-semibold"
                >
                  WhatsApp Reminder
                </a>

                {selectedCustomerId === c.id ? (
                  <div className="flex gap-1.5 items-center">
                    <input
                      type="number"
                      placeholder="₹ Paid"
                      value={repayAmount}
                      onChange={(e) => setRepayAmount(e.target.value)}
                      className="w-20 px-2 py-1 bg-slate-900 border border-slate-700 rounded text-xs text-white text-right"
                    />
                    <button
                      onClick={() => recordPayment(c.id)}
                      className="px-2.5 py-1 bg-sky-600 hover:bg-sky-500 rounded text-xs font-semibold text-white"
                    >
                      Confirm
                    </button>
                    <button
                      onClick={() => setSelectedCustomerId(null)}
                      className="px-2 py-1 bg-slate-800 text-xs text-slate-400 rounded"
                    >
                      ✕
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setSelectedCustomerId(c.id)}
                    className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-semibold border border-slate-700"
                  >
                    Receive Payment
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CustomerUdharKhata;
