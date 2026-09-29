import React, { useState, useMemo } from 'react';

/**
 * @name InventoryStockTable
 * @domain shopkeeper
 * @description Retail inventory stock tracking table featuring SKU management, real-time quantity monitoring, low-stock threshold triggers, and fast restock increments.
 * @capability inventory-management, stock-tracking, sku-table, low-stock-alerts, restock
 * @author Nexus Seed Registry Team
 */

export interface InventoryItem {
  sku: string;
  name: string;
  category: string;
  currentStock: number;
  minThreshold: number;
  unitPrice: number;
  unit: string;
}

export interface InventoryStockTableProps {
  initialItems?: InventoryItem[];
  onRestockOrder?: (item: InventoryItem, quantity: number) => void;
  className?: string;
}

const DEFAULT_INVENTORY: InventoryItem[] = [
  { sku: 'RICE-BAS-01', name: 'Basmati Rice 5kg', category: 'Grains', currentStock: 14, minThreshold: 10, unitPrice: 420, unit: 'bags' },
  { sku: 'OIL-SF-02', name: 'Sunflower Cooking Oil 1L', category: 'Edible Oils', currentStock: 4, minThreshold: 15, unitPrice: 135, unit: 'pouches' },
  { sku: 'TEA-PRM-03', name: 'Assam Gold Tea 500g', category: 'Beverages', currentStock: 22, minThreshold: 8, unitPrice: 210, unit: 'packs' },
  { sku: 'SUG-REF-04', name: 'Refined White Sugar 1kg', category: 'Staples', currentStock: 6, minThreshold: 20, unitPrice: 48, unit: 'packets' },
  { sku: 'DAL-TOOR-05', name: 'Toor Dal Premium 1kg', category: 'Pulses', currentStock: 3, minThreshold: 12, unitPrice: 160, unit: 'packets' },
];

export const InventoryStockTable: React.FC<InventoryStockTableProps> = ({
  initialItems = DEFAULT_INVENTORY,
  onRestockOrder,
  className = '',
}) => {
  const [items, setItems] = useState<InventoryItem[]>(initialItems);
  const [search, setSearch] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [filterLowStockOnly, setFilterLowStockOnly] = useState<boolean>(false);

  const categories = useMemo(() => {
    return ['All', ...Array.from(new Set(items.map((i) => i.category)))];
  }, [items]);

  const filteredItems = useMemo(() => {
    return items.filter((i) => {
      const matchCat = selectedCategory === 'All' || i.category === selectedCategory;
      const matchSearch =
        search === '' ||
        i.name.toLowerCase().includes(search.toLowerCase()) ||
        i.sku.toLowerCase().includes(search.toLowerCase());
      const matchLow = !filterLowStockOnly || i.currentStock <= i.minThreshold;
      return matchCat && matchSearch && matchLow;
    });
  }, [items, selectedCategory, search, filterLowStockOnly]);

  const adjustStock = (sku: string, delta: number) => {
    setItems((prev) =>
      prev.map((item) => {
        if (item.sku === sku) {
          const nextStock = Math.max(0, item.currentStock + delta);
          const updated = { ...item, currentStock: nextStock };
          if (delta > 0 && onRestockOrder) {
            onRestockOrder(updated, delta);
          }
          return updated;
        }
        return item;
      })
    );
  };

  const lowStockCount = useMemo(() => {
    return items.filter((i) => i.currentStock <= i.minThreshold).length;
  }, [items]);

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-3xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Inventory & Stock Catalog</h2>
          <p className="text-xs text-slate-400">Monitor warehouse and shelf inventory with automatic low-stock warnings</p>
        </div>
        {lowStockCount > 0 && (
          <span className="px-3 py-1 bg-rose-950/80 text-rose-300 border border-rose-800 text-xs font-bold rounded-full animate-pulse">
            ⚠ {lowStockCount} items below threshold
          </span>
        )}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Search by SKU or item name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-3 py-2 bg-slate-950/70 border border-slate-700 rounded-lg text-xs text-white"
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-xs px-2.5 py-1 rounded-lg text-slate-300"
        >
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <button
          onClick={() => setFilterLowStockOnly(!filterLowStockOnly)}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${
            filterLowStockOnly ? 'bg-rose-600 text-white border-rose-500' : 'bg-slate-800 text-slate-300 border-slate-700'
          }`}
        >
          {filterLowStockOnly ? 'Showing Low Stock' : 'Filter Low Stock'}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase">
              <th className="py-2.5 px-3">SKU</th>
              <th className="py-2.5 px-3">Item Name</th>
              <th className="py-2.5 px-3">Category</th>
              <th className="py-2.5 px-3">Stock Level</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3">Unit Price</th>
              <th className="py-2.5 px-3 text-right">Quick Restock</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredItems.map((item) => {
              const isLow = item.currentStock <= item.minThreshold;
              return (
                <tr key={item.sku} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-3 font-mono text-emerald-400 font-medium">{item.sku}</td>
                  <td className="py-2.5 px-3 font-semibold text-slate-200">{item.name}</td>
                  <td className="py-2.5 px-3 text-slate-400">{item.category}</td>
                  <td className="py-2.5 px-3 font-mono">
                    <span className={`font-bold ${isLow ? 'text-rose-400' : 'text-slate-200'}`}>
                      {item.currentStock}
                    </span>{' '}
                    <span className="text-slate-500 text-[10px]">{item.unit}</span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      isLow ? 'bg-rose-950/80 text-rose-300 border border-rose-800/60' : 'bg-emerald-950/60 text-emerald-300'
                    }`}>
                      {isLow ? 'LOW STOCK' : 'IN STOCK'}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-300">₹{item.unitPrice}</td>
                  <td className="py-2.5 px-3 text-right">
                    <div className="inline-flex gap-1">
                      <button
                        onClick={() => adjustStock(item.sku, -1)}
                        className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-bold"
                        title="Deduct 1 sold unit"
                      >
                        -
                      </button>
                      <button
                        onClick={() => adjustStock(item.sku, 5)}
                        className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-bold"
                        title="Add 5 restock units"
                      >
                        +5
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InventoryStockTable;
