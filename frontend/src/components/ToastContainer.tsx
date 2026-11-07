import React from 'react';
import { useAppStore } from '../store/useAppStore';
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from 'lucide-react';

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useAppStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col space-y-2 max-w-sm w-full pointer-events-none">
      {toasts.map((t) => {
        const Icon = 
          t.type === 'success' ? CheckCircle2 :
          t.type === 'error' ? AlertCircle :
          t.type === 'warning' ? AlertTriangle : Info;

        const colors = 
          t.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:text-emerald-200' :
          t.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-800 dark:text-red-200' :
          t.type === 'warning' ? 'bg-amber-500/10 border-amber-500/30 text-amber-800 dark:text-amber-200' :
          'bg-brand-500/10 border-brand-500/30 text-brand-800 dark:text-brand-200';

        const iconColor =
          t.type === 'success' ? 'text-emerald-500' :
          t.type === 'error' ? 'text-red-500' :
          t.type === 'warning' ? 'text-amber-500' :
          'text-brand-500';

        return (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-center justify-between p-3 rounded-xl border shadow-lg backdrop-blur-md bg-card/95 ${colors} transition-all animate-in slide-in-from-bottom-2 duration-200`}
          >
            <div className="flex items-center space-x-2.5">
              <Icon className={`w-4 h-4 shrink-0 ${iconColor}`} />
              <p className="text-xs font-medium">{t.message}</p>
            </div>
            <button
              onClick={() => removeToast(t.id)}
              className="p-1 rounded-md hover:bg-muted/60 text-muted-foreground hover:text-foreground shrink-0 ml-2"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
