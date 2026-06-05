import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { AlertCircle, CheckCircle2, Info, XCircle } from 'lucide-react';

const ToastContext = createContext(null);

const toastConfig = {
  success: { icon: CheckCircle2, className: 'border-emerald-200 bg-emerald-50 text-emerald-900' },
  error: { icon: XCircle, className: 'border-red-200 bg-red-50 text-red-900' },
  warning: { icon: AlertCircle, className: 'border-amber-200 bg-amber-50 text-amber-900' },
  info: { icon: Info, className: 'border-blue-200 bg-blue-50 text-blue-900' },
};

function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback(
    (type, message) => {
      const id = crypto.randomUUID();
      setToasts((current) => [...current, { id, type, message }]);
      window.setTimeout(() => removeToast(id), 3600);
    },
    [removeToast],
  );

  const value = useMemo(
    () => ({
      success: (message) => showToast('success', message),
      error: (message) => showToast('error', message),
      warning: (message) => showToast('warning', message),
      info: (message) => showToast('info', message),
    }),
    [showToast],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-[70] flex w-[min(380px,calc(100vw-32px))] flex-col gap-2">
        <AnimatePresence initial={false}>
          {toasts.map((toast) => {
            const config = toastConfig[toast.type] || toastConfig.info;
            const Icon = config.icon;
            return (
              <motion.div
                key={toast.id}
                layout
                initial={{ opacity: 0, x: 24, scale: 0.98 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 24, scale: 0.98 }}
                className={`flex items-start gap-2 rounded-md border px-3 py-2 text-sm shadow-sm ${config.className}`}
              >
                <Icon className="mt-0.5 h-4 w-4 flex-none" />
                <span>{toast.message}</span>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

export { ToastProvider, useToast };

