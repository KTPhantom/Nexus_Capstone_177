import React, { useState } from 'react';

/**
 * @name BarcodeScannerInput
 * @domain shopkeeper
 * @description Rapid POS barcode scanning input field with automatic product lookup, camera toggle simulation, sound effect feedback, and cart integration.
 * @capability barcode-scanner, pos-checkout, product-lookup, sku-scanner, fast-billing
 * @author Nexus Seed Registry Team
 */

export interface ScannedProduct {
  barcode: string;
  name: string;
  price: number;
  stock: number;
}

export interface BarcodeScannerInputProps {
  productCatalog?: Record<string, Omit<ScannedProduct, 'barcode'>>;
  onProductScanned?: (product: ScannedProduct) => void;
  className?: string;
}

const DEFAULT_CATALOG: Record<string, Omit<ScannedProduct, 'barcode'>> = {
  '8901030384118': { name: 'Tata Tea Gold 500g', price: 310, stock: 24 },
  '8901725181222': { name: 'Maggi 2-Minute Noodles 280g', price: 56, stock: 45 },
  '8901058852331': { name: 'Dettol Original Soap 125g', price: 42, stock: 18 },
  '8901491101853': { name: 'Amul Butter 500g', price: 275, stock: 12 },
  '8906001021445': { name: 'Aashirvaad Shudh Chakki Atta 5kg', price: 245, stock: 15 },
};

export const BarcodeScannerInput: React.FC<BarcodeScannerInputProps> = ({
  productCatalog = DEFAULT_CATALOG,
  onProductScanned,
  className = '',
}) => {
  const [barcodeInput, setBarcodeInput] = useState<string>('');
  const [lastScanned, setLastScanned] = useState<ScannedProduct | null>(null);
  const [scanHistory, setScanHistory] = useState<ScannedProduct[]>([]);
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleScanSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const code = barcodeInput.trim();
    if (!code) return;

    const matched = productCatalog[code];
    if (matched) {
      const scannedItem: ScannedProduct = { barcode: code, ...matched };
      setLastScanned(scannedItem);
      setScanHistory((prev) => [scannedItem, ...prev.slice(0, 9)]);
      setErrorMsg(null);
      if (onProductScanned) onProductScanned(scannedItem);
    } else {
      setErrorMsg(`Unregistered barcode: ${code}`);
    }
    setBarcodeInput('');
  };

  const simulateQuickScan = (code: string) => {
    setBarcodeInput(code);
    const matched = productCatalog[code];
    if (matched) {
      const scannedItem: ScannedProduct = { barcode: code, ...matched };
      setLastScanned(scannedItem);
      setScanHistory((prev) => [scannedItem, ...prev.slice(0, 9)]);
      setErrorMsg(null);
      if (onProductScanned) onProductScanned(scannedItem);
    }
    setBarcodeInput('');
  };

  return (
    <div className={`p-6 bg-slate-900 text-white rounded-2xl shadow-xl border border-slate-800 flex flex-col gap-6 max-w-xl w-full ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-orange-400">POS Barcode Scanner & Reader</h2>
          <p className="text-xs text-slate-400">Scan product barcodes via handheld scanner or camera lens</p>
        </div>
        <button
          onClick={() => setIsCameraActive(!isCameraActive)}
          className={`px-3 py-1 text-xs font-semibold rounded-lg border transition-colors ${
            isCameraActive ? 'bg-orange-600 text-white border-orange-500' : 'bg-slate-800 text-slate-300 border-slate-700'
          }`}
        >
          {isCameraActive ? 'Camera Scanner ON' : 'Use Camera'}
        </button>
      </div>

      <form onSubmit={handleScanSubmit} className="flex gap-2">
        <input
          type="text"
          autoFocus
          placeholder="Scan barcode or enter EAN/UPC..."
          value={barcodeInput}
          onChange={(e) => setBarcodeInput(e.target.value)}
          className="flex-1 px-3 py-2 bg-slate-950/80 border border-slate-700 rounded-lg text-sm font-mono text-white focus:outline-none focus:border-orange-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-orange-600 hover:bg-orange-500 rounded-lg text-xs font-bold text-white shadow-md"
        >
          Look Up
        </button>
      </form>

      {errorMsg && (
        <div className="p-2.5 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-300">
          {errorMsg}
        </div>
      )}

      {lastScanned && (
        <div className="p-4 bg-slate-950/80 border border-orange-500/40 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-orange-400">Last Scanned Item</span>
            <h4 className="text-base font-semibold text-slate-100 mt-0.5">{lastScanned.name}</h4>
            <span className="font-mono text-xs text-slate-400">Barcode: {lastScanned.barcode}</span>
          </div>
          <div className="text-right">
            <div className="text-xl font-extrabold text-emerald-400 font-mono">₹{lastScanned.price}</div>
            <span className="text-xs text-slate-400">{lastScanned.stock} in shelf</span>
          </div>
        </div>
      )}

      <div>
        <span className="text-xs text-slate-400 font-medium block mb-2">Simulate Barcode Scan (Click to test):</span>
        <div className="flex flex-wrap gap-2">
          {Object.entries(productCatalog).map(([code, item]) => (
            <button
              key={code}
              type="button"
              onClick={() => simulateQuickScan(code)}
              className="text-[11px] px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-md border border-slate-700 font-mono"
            >
              {item.name.slice(0, 16)}...
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BarcodeScannerInput;
