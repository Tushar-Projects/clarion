import React from 'react';
import { NavLink } from 'react-router-dom';

const LinkItem = ({ to, children }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `block px-4 py-2 rounded-lg hover:bg-white/50 dark:hover:bg-white/10 ${isActive ? 'bg-white/60 dark:bg-white/10' : ''}`
    }
  >
    {children}
  </NavLink>
);

export default function Sidebar() {
  return (
    <aside className="glass w-64 h-full p-4 sticky top-0">
      <div className="mb-6">
        <div className="text-2xl font-semibold">Clarion</div>
        <div className="text-xs opacity-70">Intelligence Console</div>
      </div>
      <nav className="space-y-1">
        <LinkItem to="/">Dashboard</LinkItem>
        <LinkItem to="/check">Check a Post</LinkItem>
        <LinkItem to="/account">Account</LinkItem>
      </nav>
      <div className="mt-8 text-xs opacity-60">
        v1.0 • glass UI
      </div>
    </aside>
  );
}
