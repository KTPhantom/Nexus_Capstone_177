import React, { useState, useMemo } from 'react';

/**
 * @name DailySalesReceipt
 * @domain shopkeeper
 * @description POS customer tax invoice and receipt generator with itemized line items, GST breakdown, customer name, payment status, and print slip layout.
 * @capability receipt-generator, billing-invoice, tax-receipt, pos-slip, customer-bill
 * @author Nexus Seed Registry Team
 */

export interface ReceiptItem {
  id: string;
  name: string;
  qty: number;
  unitPrice: number;
}

export interface DailySalesReceiptProps {
  storeName?: string;
  storeGst?: string;
  initialItems?: ReceiptItem[];
  defaultTaxRate?: number;
  onPrintInvoice?: (invoiceNumber: string, totalAmount: number) => void;
  className?: string;
}

const DEFAULT_ITEMS: ReceiptItem[] = [
  { id: 'item-1', name: 'Aashirvaad Atta 5kg', qty: 1, unitPrice: 245 },
  { id: 'item-2', name: 'Amul Pure Ghee 1L', qty: 2, unitPrice: 580 },
  { id: 'item-3', name: 'Tata Salt 1kg', qty: 3, unitPrice: 28 },
];

export const DailySalesReceipt: React.FC<DailySalesReceiptProps> = ({
  storeName = 'Gupta Super Mart & Provisions',
  storeGst = 'GSTIN: 07AAAAA0000A1Z5',
  initialItems = DEFAULT_ITEMS,
  defaultTaxRate = 5,
  onPrintInvoice,
  className = '',
}) => {
  const [items, setItems] = useState<ReceiptItem[]>(initialItems);
  const [customerName, setCustomerName] = useState<string>('Walk-in Customer');
  const [customerPhone, setCustomerPhone] = useState<string>('');
  const [discountAmount, setDiscountAmount] = useState<number>(0);
  const [invoiceNumber] = useState<string>(`INV-2026-${Math.floor(1000 + Math.random() * 9000)}`);

  const [newItemName, setNewItemName] = useState<string>('');
  const [newItemQty, setNewItemQty] = useState<number>(1);
  const [newItemPrice, setNewItemPrice] = useState<number>(50);

  const { subtotal, gstAmount, grandTotal } = useMemo(() => {
    const rawSubtotal = items.reduce((acc, it) => acc + it.qty * it.unitPrice, 0);
    const discounted = Math.max(0, rawSubtotal - discountAmount);
    const gst = discounted * (defaultTaxRate / 100);
    return {
      subtotal: rawSubtotal,
      gstAmount: Number(gst.toFixed(2)),
      grandTotal: Number((discounted + gst).toFixed(2)),
    };
  }, [items, discountAmount, defaultTaxRate]);

  const addItem = () => {
    if (!newItemName.trim() || newItemPrice <= 0 || newItemQty <= 0) return;
    const item: ReceiptItem = {
      id: `it-${Date.now()}`,
      name: newItemName.trim(),
      qty: newItemQty,
      unitPrice: newItemPrice,
    };
    setItems([...items, item]);
    setNewItemName('');
    setNewItemQty(1);
  };

  const removeItem = (id: string) => {
    setItems(items.filter((it) => it.id !== id));
  };

  const handlePrint = () => {
    if (onPrintInvoice) onPrintInvoice(invoiceNumber, grandTotal);
    window.print();
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-xl w-full ${className}`}>
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-amber-400">{storeName}</h2>
          <span className="text-[11px] font-mono text-slate-400 block">{storeGst}</span>
          <span className="text-xs text-slate-500 font-mono mt-0.5 block">{invoiceNumber} • {new Date().toLocaleDateString()}</span>
        </div>
        <button
          onClick={handlePrint}
          className="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold shadow-md"
        >
          Print Bill
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2 bg-slate-800/60 p-3 rounded-xl border border-slate-700">
        <input
          type="text"
          placeholder="Customer Name"
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
          className="px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
        />
        <input
          type="text"
          placeholder="Phone Number (for SMS receipt)"
          value={customerPhone}
          onChange={(e) => setCustomerPhone(e.target.value)}
          className="px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-white"
        />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Item Name"
          value={newItemName}
          onChange={(e) => setNewItemName(e.target.value)}
          className="flex-2 px-2.5 py-1.5 bg-slate-950/80 border border-slate-700 rounded-lg text-xs text-white"
        />
        <input
          type="number"
          min="1"
          placeholder="Qty"
          value={newItemQty}
          onChange={(e) => setNewItemQty(Math.max(1, parseInt(e.target.value) || 1))}
          className="w-16 px-2 py-1.5 bg-slate-950/80 border border-slate-700 rounded-lg text-xs text-white text-center"
        />
        <input
          type="number"
          placeholder="₹ Rate"
          value={newItemPrice}
          onChange={(e) => setNewItemPrice(Math.max(0, parseFloat(e.target.value) || 0))}
          className="w-20 px-2 py-1.5 bg-slate-950/80 border border-slate-700 rounded-lg text-xs text-white text-right"
        />
        <button
          onClick={addItem}
          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-xs font-semibold text-white"
        >
          Add
        </button>
      </div>

      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/60">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-800/80 text-slate-400 uppercase">
              <th className="py-2 px-3">Item</th>
              <th className="py-2 px-3 text-center">Qty</th>
              <th className="py-2 px-3 text-right">Price</th>
              <th className="py-2 px-3 text-right">Total</th>
              <th className="py-2 px-2 text-right"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {items.map((it) => (
              <tr key={it.id}>
                <td className="py-2 px-3 font-medium text-slate-200">{it.name}</td>
                <td className="py-2 px-3 text-center text-slate-400">{it.qty}</td>
                <td className="py-2 px-3 text-right font-mono text-slate-400">₹{it.unitPrice}</td>
                <td className="py-2 px-3 text-right font-mono font-bold text-slate-200">₹{it.qty * it.unitPrice}</td>
                <td className="py-2 px-2 text-right">
                  <button onClick={() => removeItem(it.id)} className="text-slate-500 hover:text-rose-400">×</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-col gap-1.5 text-xs text-slate-400 border-t border-slate-800 pt-3">
        <div className="flex justify-between">
          <span>Subtotal</span>
          <span className="font-mono text-white">₹{subtotal}</span>
        </div>
        <div className="flex justify-between items-center">
          <span>Discount (₹)</span>
          <input
            type="number"
            value={discountAmount}
            onChange={(e) => setDiscountAmount(Math.max(0, parseFloat(e.target.value) || 0))}
            className="w-20 px-2 py-0.5 bg-slate-800 border border-slate-700 rounded text-right font-mono text-white text-xs"
          />
        </div>
        <div className="flex justify-between">
          <span>GST ({defaultTaxRate}%)</span>
          <span className="font-mono text-white">₹{gstAmount}</span>
        </div>
        <div className="flex justify-between text-base font-bold text-white border-t border-slate-800 pt-2 mt-1">
          <span className="text-amber-400">Grand Total</span>
          <span className="text-emerald-400 font-mono">₹{grandTotal}</span>
        </div>
      </div>
    </div>
  );
};

export default DailySalesReceipt;
