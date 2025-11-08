import React from 'react';

export default function GlassCard({ className='', children, highlight=false }) {
  return (
    <div className={`glass ${highlight ? 'gradient-border' : ''} ${className}`}>
      {children}
    </div>
  );
}
