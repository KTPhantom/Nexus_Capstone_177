import React, { useState, useMemo } from 'react';

/**
 * @name SupplierContactList
 * @domain shopkeeper
 * @description Wholesale distributor and vendor directory with direct contact links, pending balance ledgers, delivery schedule logs, and payment terms.
 * @capability supplier-directory, vendor-contacts, wholesale-orders, distributor-ledger
 * @author Nexus Seed Registry Team
 */

export interface Supplier {
  id: string;
  name: string;
  category: string;
  phone: string;
  whatsapp: string;
  paymentTerms: string;
  pendingBalance: number;
  lastDelivery: string;
}

export interface SupplierContactListProps {
  initialSuppliers?: Supplier[];
  onCallSupplier?: (supplier: Supplier) => void;
  className?: string;
}

const DEFAULT_SUPPLIERS: Supplier[] = [
  { id: 'sup-1', name: 'Krishna Wholesale Grains', category: 'Grains & Pulses', phone: '+91 98765 43210', whatsapp: '919876543210', paymentTerms: 'Net 15 Days', pendingBalance: 12400, lastDelivery: '2026-09-24' },
  { id: 'sup-2', name: 'Apex Edible Oils & FMCG', category: 'Oils & Packaged Food', phone: '+91 98111 22334', whatsapp: '919811122334', paymentTerms: 'Cash On Delivery', pendingBalance: 0, lastDelivery: '2026-09-26' },
  { id: 'sup-3', name: 'Modern Dairy Distributors', category: 'Dairy & Beverages', phone: '+91 98450 11223', whatsapp: '919845011223', paymentTerms: 'Weekly Settlement', pendingBalance: 3850, lastDelivery: '2026-09-27' },
  { id: 'sup-4', name: 'Standard Spices & Condiments', category: 'Spices', phone: '+91 97123 45678', whatsapp: '919712345678', paymentTerms: 'Net 30 Days', pendingBalance: 8200, lastDelivery: '2026-09-18' },
];

export const SupplierContactList: React.FC<SupplierContactListProps> = ({
  initialSuppliers = DEFAULT_SUPPLIERS,
  onCallSupplier,
  className = '',
}) => {
  const [suppliers] = useState<Supplier[]>(initialSuppliers);
  const [search, setSearch] = useState<string>('');

  const filtered = useMemo(() => {
    return suppliers.filter(
      (s) =>
        s.name.toLowerCase().includes(search.toLowerCase()) ||
        s.category.toLowerCase().includes(search.toLowerCase()) ||
        s.phone.includes(search)
    );
  }, [suppliers, search]);

  const totalPayable = useMemo(() => {
    return suppliers.reduce((acc, s) => acc + s.pendingBalance, 0);
  }, [suppliers]);

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-2xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Supplier & Distributor Contacts</h2>
          <p className="text-xs text-slate-400">Directly contact wholesale distributors and track pending payables</p>
        </div>
        <div className="text-right">
          <span className="text-[10px] uppercase tracking-wider text-slate-400">Total Payable</span>
          <div className="text-xl font-bold text-rose-400">₹{totalPayable.toLocaleString()}</div>
        </div>
      </div>

      <input
        type="text"
        placeholder="Search supplier by business name or category..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-3 py-2 bg-slate-950/70 border border-slate-700 rounded-lg text-xs text-white"
      />

      <div className="flex flex-col gap-3">
        {filtered.map((s) => (
          <div
            key={s.id}
            className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl flex items-center justify-between hover:border-sky-500/40 transition-colors"
          >
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-slate-200">{s.name}</h3>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-medium">
                  {s.category}
                </span>
              </div>
              <div className="flex gap-4 text-xs text-slate-400 mt-1">
                <span>Terms: <strong className="text-slate-300">{s.paymentTerms}</strong></span>
                <span>Last Supply: <strong className="text-slate-300">{s.lastDelivery}</strong></span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <span className="text-[10px] text-slate-400 block uppercase">Due Balance</span>
                <span className={`text-sm font-bold font-mono ${s.pendingBalance > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  ₹{s.pendingBalance.toLocaleString()}
                </span>
              </div>

              <div className="flex gap-1.5">
                <a
                  href={`tel:${s.phone}`}
                  onClick={() => onCallSupplier && onCallSupplier(s)}
                  className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700"
                >
                  Call
                </a>
                <a
                  href={`https://wa.me/${s.whatsapp}?text=Hello%20${encodeURIComponent(s.name)},%20checking%20order%20status`}
                  target="_blank"
                  rel="noreferrer"
                  className="px-2.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg"
                >
                  WhatsApp
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SupplierContactList;
