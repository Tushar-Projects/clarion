import React from 'react';
import Sidebar from './Sidebar';
import ThemeToggle from './ThemeToggle';

export default function AppShell({ children }) {
  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f7f8fc,transparent),linear-gradient(0deg,#ffffff,transparent)] dark:bg-[linear-gradient(180deg,#0b0b0c,transparent),linear-gradient(0deg,#111213,transparent)]">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-[16rem_1fr] gap-6">
          <Sidebar />
          <div className="space-y-6">
            <header className="flex items-center justify-between">
              <h1 className="text-xl font-semibold">Today</h1>
              <ThemeToggle />
            </header>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
