import type { ReactNode } from 'react';

export type IconName = 'home' | 'book' | 'practice' | 'progress' | 'arrow' | 'check';

export function Icon({ name, className = '' }: { name: IconName; className?: string }) {
  const paths: Record<IconName, ReactNode> = {
    home: <><path d="m3 10 9-7 9 7" /><path d="M5 9v11h5v-6h4v6h5V9" /></>,
    book: <><path d="M12 5v15M3 4h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5v15h-5a4 4 0 0 0-4 2 4 4 0 0 0-4-2H3Z" /></>,
    practice: <><rect x="5" y="4" width="14" height="17" rx="2" /><path d="M9 4V2h6v2M9 10h6M9 14h3M9 18h6" /></>,
    progress: <><path d="M4 3v17h17M8 15l4-5 4 2 5-7" /><path d="M17 5h4v4" /></>,
    arrow: <><path d="M20 12H4m7-7-7 7 7 7" /></>,
    check: <path d="m5 12 4 4L19 6" />,
  };
  return <svg className={`icon ${className}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">{paths[name]}</svg>;
}
