// Notification Component
'use client';
import { Toaster } from 'react-hot-toast';

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Toaster position="top-right" />
      {children}
    </>
  );
}
