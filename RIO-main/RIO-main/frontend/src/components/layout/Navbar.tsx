'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Waves, BarChart2, Map, Database, Download, Radio, Info, Settings, Play, Mountain } from 'lucide-react';
import { useState } from 'react';

const NAV_ITEMS = [
  { href: '/', label: 'Dashboard', icon: Map },
  { href: '/flood-3d', label: '3D Flood', icon: Mountain },
  { href: '/demo', label: 'Demo', icon: Play },
  { href: '/simulations', label: 'Simulations', icon: BarChart2 },
  { href: '/data', label: 'Data', icon: Database },
  { href: '/exports', label: 'Exports', icon: Download },
  { href: '/monitoring', label: 'Monitoring', icon: Radio },
  { href: '/about', label: 'About', icon: Info },
];

export default function Navbar() {
  const pathname = usePathname();
  const [theme, setTheme] = useState<'dark'|'light'>('dark');
  // full implementation with mobile menu, model status pills, theme toggle
  // Model status: SPH [MOCK] Delft3D [MOCK] shown as small pills
  return (
    <nav className="fixed top-0 z-50 w-full border-b border-slate-800 bg-slate-950/95 backdrop-blur">
      <div className="flex h-14 items-center px-4 gap-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-bold text-cyan-400 shrink-0">
          <Waves className="h-6 w-6" />
          <span className="hidden sm:block">HADR Platform</span>
        </Link>
        {/* Nav links */}
        <div className="flex-1 flex items-center gap-1 overflow-x-auto">
          {NAV_ITEMS.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
                pathname === item.href
                  ? 'bg-cyan-600/20 text-cyan-400'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <item.icon className="h-3.5 w-3.5" />
              <span className="hidden md:block">{item.label}</span>
            </Link>
          ))}
        </div>
        {/* Right side: model status + theme */}
        <div className="flex items-center gap-2 shrink-0">
          <span className="hidden lg:flex items-center gap-1 px-2 py-1 rounded text-xs bg-violet-900/40 text-violet-300 border border-violet-700/50">
            SPH <span className="text-violet-400 font-bold">MOCK</span>
          </span>
          <span className="hidden lg:flex items-center gap-1 px-2 py-1 rounded text-xs bg-blue-900/40 text-blue-300 border border-blue-700/50">
            Delft3D <span className="text-blue-400 font-bold">MOCK</span>
          </span>
          <Link href="/settings" className="p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800">
            <Settings className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </nav>
  );
}
