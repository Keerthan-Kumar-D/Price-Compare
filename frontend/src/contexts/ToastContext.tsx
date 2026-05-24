import React, { createContext, useContext, useState, useCallback } from 'react';
import { ToastContainer } from '../components/Toast';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning';
  message: string;
}

interface ToastContextType {
  showToast: (type: 'success' | 'error' | 'warning', message: string) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: React.ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((type: 'success' | 'error' | 'warning', message: string) => {
    const id = Date.now().toString();
    const newToast: Toast = { id, type, message };
    
    setToasts(prev => [...prev, newToast]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
};