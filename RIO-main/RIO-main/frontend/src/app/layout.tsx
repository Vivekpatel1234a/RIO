import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/layout/Navbar';
import DemoBanner from '@/components/layout/DemoBanner';
import QueryProvider from '@/components/providers/QueryProvider';

const inter = { className: "" };

export const metadata: Metadata = {
  title: 'HADR Flood Simulation Platform',
  description: 'Dam-break analysis, flood inundation simulation, and HADR decision support',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-slate-950 text-slate-100 min-h-screen`}>
        <QueryProvider>
          <Navbar />
          <DemoBanner />
          <main className="pt-14">{children}</main>
        </QueryProvider>
      </body>
    </html>
  );
}
