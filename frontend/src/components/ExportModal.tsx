import { useState } from 'react';
import { X, FileText, Globe, Presentation, ArrowRight } from 'lucide-react';
import clsx from 'clsx';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  datasetName?: string;
}

export function ExportModal({ isOpen, onClose }: ExportModalProps) {
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'html' | 'pptx'>('pdf');
  const [isExporting, setIsExporting] = useState(false);

  if (!isOpen) return null;

  const handleExport = () => {
    setIsExporting(true);
    setTimeout(() => {
      setIsExporting(false);
      if (selectedFormat === 'pdf') {
        window.print();
      } else {
        alert(`Exporting ${selectedFormat.toUpperCase()} package...`);
      }
      onClose();
    }, 800);
  };

  const options = [
    {
      id: 'pdf',
      title: 'PDF',
      subtitle: 'Full analysis report',
      icon: FileText,
      iconColor: 'text-red-400',
      iconBg: 'bg-red-500/10'
    },
    {
      id: 'html',
      title: 'HTML',
      subtitle: 'Interactive report',
      icon: Globe,
      iconColor: 'text-blue-400',
      iconBg: 'bg-blue-500/10'
    },
    {
      id: 'pptx',
      title: 'PPTX',
      subtitle: 'Presentation format',
      icon: Presentation,
      iconColor: 'text-orange-400',
      iconBg: 'bg-orange-500/10'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#0f172a] border border-[#1e293b] rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-5">
        <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">Export Report</h3>
            <p className="text-xs text-slate-400 mt-0.5">Choose the format for your report.</p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 3 Format Options Grid */}
        <div className="grid grid-cols-3 gap-3">
          {options.map((opt) => {
            const isSelected = selectedFormat === opt.id;
            const Icon = opt.icon;
            return (
              <button
                key={opt.id}
                type="button"
                onClick={() => setSelectedFormat(opt.id as any)}
                className={clsx(
                  "p-3 rounded-xl border text-center flex flex-col items-center justify-center transition-all relative",
                  isSelected
                    ? "bg-[#1e293b] border-[#6366f1] ring-1 ring-[#6366f1]/50 shadow-lg shadow-indigo-500/10"
                    : "bg-[#0b1326] border-[#1e293b] hover:border-slate-700 text-slate-400"
                )}
              >
                {/* Radio selection dot in top right */}
                <div className="absolute top-2 right-2">
                  <div className={clsx(
                    "w-3 h-3 rounded-full border flex items-center justify-center",
                    isSelected ? "border-[#6366f1] bg-[#6366f1]" : "border-slate-600"
                  )}>
                    {isSelected && <div className="w-1 h-1 rounded-full bg-white" />}
                  </div>
                </div>

                <div className={clsx("p-2 rounded-lg mb-2", opt.iconBg, opt.iconColor)}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className="font-bold text-sm text-white">{opt.title}</span>
                <span className="text-[10px] text-slate-400 mt-0.5 leading-tight">{opt.subtitle}</span>
              </button>
            );
          })}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#1e293b]">
          <button
            onClick={onClose}
            type="button"
            className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleExport}
            disabled={isExporting}
            type="button"
            className="px-5 py-2 text-xs font-semibold text-white bg-gradient-to-r from-[#6366f1] to-[#4f46e5] hover:from-[#5558e6] hover:to-[#4338ca] rounded-xl shadow-md shadow-indigo-500/25 flex items-center gap-1.5 transition-all disabled:opacity-50"
          >
            <span>{isExporting ? 'Exporting...' : 'Export'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
