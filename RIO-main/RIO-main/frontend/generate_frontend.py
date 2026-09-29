import os

files = {
"src/lib/api.ts": """import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

export const loadDemo = () => api.post('/api/demo/load');
export const getDemoStatus = (id: string) => api.get(`/api/demo/status/${id}`);
export const getDemoFull = () => api.get('/api/demo/full');
export const getDemoRiver = () => api.get('/api/demo/river');
export const getDemoDam = () => api.get('/api/demo/dam');
export const getDemoReservoir = () => api.get('/api/demo/reservoir');
export const getDemoHydrology = () => api.get('/api/demo/hydrology');
export const getDemoSettlements = () => api.get('/api/demo/settlements');
export const getDemoRoads = () => api.get('/api/demo/roads');
export const getDemoStudyArea = () => api.get('/api/demo/study-area');
export const getDemoDEMInfo = () => api.get('/api/demo/dem-info');
export const getSimulations = () => api.get('/api/simulations');
export const getSimulation = (id: string) => api.get(`/api/simulations/${id}`);
export const runSimulation = (id: string) => api.post(`/api/simulations/${id}/run`);
export const getSimulationStatus = (id: string) => api.get(`/api/simulations/${id}/status`);
export const getSimulationResults = (id: string) => api.get(`/api/simulations/${id}/results`);
export const getSimulationComparison = (id: string) => api.get(`/api/simulations/${id}/comparison`);
export const getSimulationImpact = (id: string) => api.get(`/api/simulations/${id}/impact`);
export const getSimulationExports = (id: string) => api.get(`/api/simulations/${id}/exports`);
export const createSimulation = (params: object) => api.post('/api/simulations', params);
export const getModels = () => api.get('/api/models');
export const getHealth = () => api.get('/api/health');
export const getMonitoringStatus = () => api.get('/api/monitoring/status');
export const getAlerts = () => api.get('/api/monitoring/alerts');
export const getGEEStatus = () => api.get('/api/gee/status');
export const getExports = () => api.get('/api/exports');
""",

"src/types/index.ts": """export type SimulationStatus = 'CREATED' | 'VALIDATING' | 'PREPROCESSING' | 'GENERATING_INPUT' | 'SPH_RUNNING' | 'DELFT3D_RUNNING' | 'POSTPROCESSING' | 'IMPACT_ANALYSIS' | 'EXPORTING' | 'COMPLETED' | 'FAILED';

export interface PipelineStage { stage_id: string; message: string; progress: number; done: boolean; timestamp: string; }
export interface SimulationJobStatus { simulation_id: string; status: SimulationStatus; progress: number; current_stage: string; stages: PipelineStage[]; error?: string; is_mock: boolean; }
export interface FloodResult { model: string; is_mock: boolean; disclaimer: string; max_depth_m: number; avg_depth_m: number; max_velocity_ms: number; inundation_area_km2: number; peak_discharge_m3s: number; arrival_time_hrs: number; output_dir: string; file_paths: Record<string, string>; }
export interface ImpactResult { model: string; is_mock: boolean; is_preliminary: boolean; disclaimer: string; affected_population: number; affected_villages: number; affected_buildings: number; affected_roads_km: number; affected_bridges: number; affected_agriculture_ha: number; affected_infrastructure: number; impact_categories: Record<string, { applicable: boolean; area_fraction?: number; estimated_area_km2?: number }>; flood_area_km2: number; max_depth_m: number; }
export interface ComparisonMetric { sph: number; delft3d: number; difference: number; pct_difference: number; }
export interface ModelComparison { is_mock: boolean; disclaimer: string; metrics: { inundation_area_km2: ComparisonMetric; max_depth_m: ComparisonMetric; avg_depth_m: ComparisonMetric; max_velocity_ms: ComparisonMetric; peak_discharge_m3s: ComparisonMetric; arrival_time_hrs: ComparisonMetric; affected_population: ComparisonMetric; }; }
export interface HydrologyPoint { timestamp: string; hour: number; discharge_m3s: number; water_level_m: number; rainfall_mm_hr: number; velocity_ms: number; stage: string; is_demo: boolean; }
export interface DamInfo { name: string; type: string; coordinates: [number, number]; height_m: number; reservoir_elevation_m: number; reservoir_area_km2: number; reservoir_volume_mcm: number; normal_water_level_m: number; max_water_level_m: number; is_demo: boolean; }
export interface ModelStatus { model_name: string; full_name: string; adapter_status: string; execution_mode: string; is_mock: boolean; real_solver_connected: boolean; disclaimer: string; }
""",

"src/components/ui/badge.tsx": """'use client';
import { cn } from '@/lib/utils';
const variants = {
  default: 'bg-primary/15 text-primary border-primary/30',
  secondary: 'bg-muted text-muted-foreground',
  destructive: 'bg-red-500/15 text-red-500 border-red-500/30',
  success: 'bg-green-500/15 text-green-600 border-green-500/30',
  warning: 'bg-amber-500/15 text-amber-600 border-amber-500/30',
  mock: 'bg-violet-500/15 text-violet-600 border-violet-500/30',
  demo: 'bg-cyan-500/15 text-cyan-600 border-cyan-500/30',
  outline: 'bg-transparent border text-foreground',
};
export function Badge({ children, variant='default', className }: { children: React.ReactNode; variant?: keyof typeof variants; className?: string }) {
  return <span className={cn('inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold', variants[variant], className)}>{children}</span>;
}
""",

"src/components/ui/button.tsx": """'use client';
import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';
import React from 'react';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50 disabled:pointer-events-none',
  {
    variants: {
      variant: {
        default: 'bg-cyan-600 text-white hover:bg-cyan-700',
        secondary: 'bg-slate-700 text-white hover:bg-slate-600',
        outline: 'border border-slate-600 text-slate-300 hover:bg-slate-800',
        ghost: 'text-slate-300 hover:bg-slate-800',
        destructive: 'bg-red-600 text-white hover:bg-red-700',
        success: 'bg-green-600 text-white hover:bg-green-700',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-9 px-4',
        lg: 'h-11 px-6 text-base',
        xl: 'h-14 px-8 text-lg',
        icon: 'h-9 w-9',
      },
    },
    defaultVariants: { variant: 'default', size: 'md' },
  }
);

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants>;
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, ...props }, ref) => (
  <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
));
Button.displayName = 'Button';
export { buttonVariants };
""",

"src/components/ui/card.tsx": """import { cn } from '@/lib/utils';
export const Card = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('rounded-lg border border-slate-700 bg-slate-900/80 shadow-sm', className)} {...props} />
);
export const CardHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex flex-col space-y-1.5 p-5', className)} {...props} />
);
export const CardTitle = ({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h3 className={cn('text-lg font-semibold leading-none tracking-tight text-white', className)} {...props} />
);
export const CardDescription = ({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
  <p className={cn('text-sm text-slate-400', className)} {...props} />
);
export const CardContent = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('p-5 pt-0', className)} {...props} />
);
export const CardFooter = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex items-center p-5 pt-0', className)} {...props} />
);
""",

"src/components/ui/progress.tsx": """'use client';

import * as React from 'react';
import * as ProgressPrimitive from '@radix-ui/react-progress';
import { cn } from '@/lib/utils';

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
>(({ className, value, ...props }, ref) => (
  <ProgressPrimitive.Root
    ref={ref}
    className={cn('relative h-2 w-full overflow-hidden rounded-full bg-slate-800', className)}
    {...props}
  >
    <ProgressPrimitive.Indicator
      className="h-full w-full flex-1 bg-cyan-500 transition-all"
      style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
    />
  </ProgressPrimitive.Root>
));
Progress.displayName = ProgressPrimitive.Root.displayName;

export { Progress };
""",

"src/components/ui/tabs.tsx": """'use client';

import * as React from 'react';
import * as TabsPrimitive from '@radix-ui/react-tabs';
import { cn } from '@/lib/utils';

const Tabs = TabsPrimitive.Root;

const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      'inline-flex h-9 items-center justify-center rounded-lg bg-slate-800 p-1 text-slate-400',
      className
    )}
    {...props}
  />
));
TabsList.displayName = TabsPrimitive.List.displayName;

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-slate-950 data-[state=active]:text-slate-50 data-[state=active]:shadow',
      className
    )}
    {...props}
  />
));
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName;

const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      'mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
      className
    )}
    {...props}
  />
));
TabsContent.displayName = TabsPrimitive.Content.displayName;

export { Tabs, TabsList, TabsTrigger, TabsContent };
""",

"src/components/ui/separator.tsx": """'use client';

import * as React from 'react';
import * as SeparatorPrimitive from '@radix-ui/react-separator';
import { cn } from '@/lib/utils';

const Separator = React.forwardRef<
  React.ElementRef<typeof SeparatorPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SeparatorPrimitive.Root>
>(
  (
    { className, orientation = 'horizontal', decorative = true, ...props },
    ref
  ) => (
    <SeparatorPrimitive.Root
      ref={ref}
      decorative={decorative}
      orientation={orientation}
      className={cn(
        'shrink-0 bg-slate-800',
        orientation === 'horizontal' ? 'h-[1px] w-full' : 'h-full w-[1px]',
        className
      )}
      {...props}
    />
  )
);
Separator.displayName = SeparatorPrimitive.Root.displayName;

export { Separator };
""",

"src/components/layout/Navbar.tsx": """'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Waves, BarChart2, Map, Database, Download, Radio, Info, Settings, Play, Moon, Sun } from 'lucide-react';
import { useState } from 'react';

const NAV_ITEMS = [
  { href: '/', label: 'Dashboard', icon: Map },
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
""",

"src/components/layout/DemoBanner.tsx": """'use client';
import { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';
export default function DemoBanner() {
  const [dismissed, setDismissed] = useState(false);
  if (dismissed) return null;
  return (
    <div className="fixed top-14 z-40 w-full bg-amber-900/80 border-b border-amber-700/60 backdrop-blur">
      <div className="flex items-center gap-3 px-4 py-2 text-sm text-amber-200">
        <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
        <span className="flex-1 text-xs">
          <strong>DEMONSTRATION MODE:</strong> This demonstration uses synthetic terrain, hydrology, infrastructure data and simplified mock hydraulic models. The outputs are for software demonstration and workflow validation only and must not be used for real-world emergency or engineering decisions.
        </span>
        <button onClick={() => setDismissed(true)} className="shrink-0 text-amber-400 hover:text-amber-200">
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
""",

"src/components/map/FloodMap.tsx": """'use client';
import { useEffect, useRef, useState } from 'react';
import type { Map as MapLibreMap, GeoJSONSource } from 'maplibre-gl';
import { Layers, Eye, EyeOff } from 'lucide-react';

interface FloodMapProps {
  riverGeoJSON?: object;
  damLocation?: [number, number];
  reservoirGeoJSON?: object;
  settlementsGeoJSON?: object;
  roadsGeoJSON?: object;
  floodExtentGeoJSON?: object;
  onMapLoad?: (map: MapLibreMap) => void;
}

export default function FloodMap(props: FloodMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [layerVisibility, setLayerVisibility] = useState<Record<string, boolean>>({
    river: true,
    reservoir: true,
    settlements: true,
    roads: true,
    flood: true,
  });

  useEffect(() => {
    if (!mapContainerRef.current) return;
    let MapLibre: typeof import('maplibre-gl');
    import('maplibre-gl').then((ml) => {
      MapLibre = ml;
      const map = new ml.default.Map({
        container: mapContainerRef.current!,
        style: {
          version: 8,
          sources: {
            'carto': {
              type: 'raster',
              tiles: ['https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '&copy; CartoDB &copy; OpenStreetMap',
            }
          },
          layers: [{ id: 'background', type: 'raster', source: 'carto' }]
        },
        center: [79.95, 30.30],
        zoom: 10,
      });
      map.on('load', () => {
        mapRef.current = map;
        setLoaded(true);
        if (props.onMapLoad) props.onMapLoad(map);
      });
      return () => { map.remove(); mapRef.current = null; };
    });
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loaded) return;
    // Add/update river layer
    if (props.riverGeoJSON) {
      if (map.getSource('river')) {
        (map.getSource('river') as GeoJSONSource).setData(props.riverGeoJSON as any);
      } else {
        map.addSource('river', { type: 'geojson', data: props.riverGeoJSON as any });
        map.addLayer({ id: 'river-line', type: 'line', source: 'river',
          filter: ['==', ['get', 'type'], 'river_centerline'],
          paint: { 'line-color': '#0EA5E9', 'line-width': 2.5 } });
        map.addLayer({ id: 'river-poly', type: 'fill', source: 'river',
          filter: ['==', ['get', 'type'], 'river_polygon'],
          paint: { 'fill-color': '#0EA5E9', 'fill-opacity': 0.25 } });
      }
    }
    // Add dam marker
    if (props.damLocation) {
      if (!map.getSource('dam')) {
        map.addSource('dam', { type: 'geojson', data: { type: 'FeatureCollection', features: [{ type: 'Feature', geometry: { type: 'Point', coordinates: props.damLocation }, properties: { name: 'Demo Dam' } }] } });
        map.addLayer({ id: 'dam-point', type: 'circle', source: 'dam', paint: { 'circle-radius': 8, 'circle-color': '#EF4444', 'circle-stroke-width': 2, 'circle-stroke-color': '#fff' } });
      }
    }
    // Add reservoir
    if (props.reservoirGeoJSON) {
      if (map.getSource('reservoir')) {
        (map.getSource('reservoir') as GeoJSONSource).setData(props.reservoirGeoJSON as any);
      } else {
        map.addSource('reservoir', { type: 'geojson', data: props.reservoirGeoJSON as any });
        map.addLayer({ id: 'reservoir-fill', type: 'fill', source: 'reservoir', paint: { 'fill-color': '#38BDF8', 'fill-opacity': 0.4 } });
        map.addLayer({ id: 'reservoir-line', type: 'line', source: 'reservoir', paint: { 'line-color': '#38BDF8', 'line-width': 1.5 } });
      }
    }
    // Add settlements
    if (props.settlementsGeoJSON) {
      if (map.getSource('settlements')) {
        (map.getSource('settlements') as GeoJSONSource).setData(props.settlementsGeoJSON as any);
      } else {
        map.addSource('settlements', { type: 'geojson', data: props.settlementsGeoJSON as any });
        map.addLayer({ id: 'settlements-circle', type: 'circle', source: 'settlements', paint: { 'circle-radius': 6, 'circle-color': '#F59E0B', 'circle-stroke-width': 1.5, 'circle-stroke-color': '#fff' } });
      }
    }
    // Add roads
    if (props.roadsGeoJSON) {
      if (map.getSource('roads')) {
        (map.getSource('roads') as GeoJSONSource).setData(props.roadsGeoJSON as any);
      } else {
        map.addSource('roads', { type: 'geojson', data: props.roadsGeoJSON as any });
        map.addLayer({ id: 'roads-line', type: 'line', source: 'roads', paint: { 'line-color': '#94A3B8', 'line-width': 1.5 } });
      }
    }
    // Add flood extent
    if (props.floodExtentGeoJSON) {
      if (map.getSource('flood')) {
        (map.getSource('flood') as GeoJSONSource).setData(props.floodExtentGeoJSON as any);
      } else {
        map.addSource('flood', { type: 'geojson', data: props.floodExtentGeoJSON as any });
        map.addLayer({ id: 'flood-fill', type: 'fill', source: 'flood', paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.55 } });
        map.addLayer({ id: 'flood-line', type: 'line', source: 'flood', paint: { 'line-color': '#F97316', 'line-width': 1 } });
      }
    }
  }, [loaded, props.riverGeoJSON, props.damLocation, props.reservoirGeoJSON, props.settlementsGeoJSON, props.roadsGeoJSON, props.floodExtentGeoJSON]);

  const toggleLayer = (layer: string) => {
    const map = mapRef.current;
    if (!map || !loaded) return;
    const newVisible = !layerVisibility[layer];
    const layerIds: Record<string, string[]> = {
      river: ['river-line', 'river-poly'],
      reservoir: ['reservoir-fill', 'reservoir-line'],
      settlements: ['settlements-circle'],
      roads: ['roads-line'],
      flood: ['flood-fill', 'flood-line'],
    };
    (layerIds[layer] || []).forEach(id => {
      if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', newVisible ? 'visible' : 'none');
    });
    setLayerVisibility(prev => ({ ...prev, [layer]: newVisible }));
  };

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainerRef} className="absolute inset-0" />
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-900">
          <div className="text-cyan-400 animate-pulse">Loading map...</div>
        </div>
      )}
      {/* Layer controls */}
      <div className="absolute top-4 right-4 bg-slate-900/90 rounded-lg border border-slate-700 p-3 text-xs space-y-2">
        <div className="flex items-center gap-1.5 text-slate-300 font-medium mb-1">
          <Layers className="h-3.5 w-3.5" /> Layers
        </div>
        {Object.entries(layerVisibility).map(([layer, visible]) => (
          <button key={layer} onClick={() => toggleLayer(layer)}
            className="flex items-center gap-2 text-slate-400 hover:text-white w-full">
            {visible ? <Eye className="h-3 w-3 text-cyan-400" /> : <EyeOff className="h-3 w-3" />}
            <span className="capitalize">{layer}</span>
          </button>
        ))}
      </div>
      {/* Legend */}
      <div className="absolute bottom-8 left-4 bg-slate-900/90 rounded-lg border border-slate-700 p-3 text-xs">
        <div className="text-slate-300 font-medium mb-2">Flood Depth</div>
        {[['#FFF176','0–0.5m'],['#FFB300','0.5–1m'],['#F57C00','1–2m'],['#D32F2F','2–5m'],['#7B1FA2','>5m']].map(([color, label]) => (
          <div key={label} className="flex items-center gap-2 text-slate-400">
            <span className="w-4 h-3 rounded" style={{background:color}} />{label}
          </div>
        ))}
        <div className="mt-1 text-amber-400 text-[10px]">MOCK DATA</div>
      </div>
    </div>
  );
}
""",

"src/components/demo/DemoRunButton.tsx": """'use client';
import { useState, useEffect, useRef } from 'react';
import { Play, CheckCircle, XCircle, Loader2, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { loadDemo, getDemoStatus } from '@/lib/api';
import { useRouter } from 'next/navigation';
import type { SimulationJobStatus, PipelineStage } from '@/types';

const STAGE_LABELS: Record<string, string> = {
  CREATED: '01 — Data Loading',
  VALIDATING: '02 — Data Validation',
  PREPROCESSING: '03 — GIS Preprocessing',
  GENERATING_INPUT: '04 — Model Input Generation',
  SPH_RUNNING: '05 — Mock SPH Simulation',
  DELFT3D_RUNNING: '06 — Mock Delft3D Simulation',
  POSTPROCESSING: '07 — Post-Processing',
  IMPACT_ANALYSIS: '08 — Impact Analysis',
  EXPORTING: '09 — GIS Export',
  COMPLETED: '10 — Complete',
};

export default function DemoRunButton() {
  const [running, setRunning] = useState(false);
  const [simulationId, setSimulationId] = useState<string|null>(null);
  const [status, setStatus] = useState<SimulationJobStatus|null>(null);
  const [error, setError] = useState<string|null>(null);
  const router = useRouter();
  const pollRef = useRef<NodeJS.Timeout|null>(null);

  const startDemo = async () => {
    setRunning(true);
    setError(null);
    setStatus(null);
    try {
      const res = await loadDemo();
      const simId = res.data.simulation_id;
      setSimulationId(simId);
      // Poll status
      const poll = async () => {
        try {
          const statusRes = await getDemoStatus(simId);
          const s = statusRes.data as SimulationJobStatus;
          setStatus(s);
          if (s.status !== 'COMPLETED' && s.status !== 'FAILED') {
            pollRef.current = setTimeout(poll, 2000);
          } else {
            setRunning(false);
          }
        } catch (e) {
          setError('Failed to get status');
          setRunning(false);
        }
      };
      poll();
    } catch (e: any) {
      setError(e?.message || 'Failed to start demo');
      setRunning(false);
    }
  };

  useEffect(() => () => { if (pollRef.current) clearTimeout(pollRef.current); }, []);

  const isCompleted = status?.status === 'COMPLETED';
  const isFailed = status?.status === 'FAILED';
  const progress = status?.progress || 0;

  return (
    <div className="space-y-6">
      {!running && !isCompleted && !isFailed && (
        <Button size="xl" className="bg-cyan-600 hover:bg-cyan-500 text-white font-bold shadow-lg shadow-cyan-900/50" onClick={startDemo}>
          <Play className="h-6 w-6" fill="currentColor" />
          RUN FULL DEMO
        </Button>
      )}

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm">
          <XCircle className="h-4 w-4" />{error}
          <Button size="sm" variant="outline" onClick={startDemo}>Retry</Button>
        </div>
      )}

      {(running || isCompleted || isFailed) && status && (
        <div className="bg-slate-900 rounded-xl border border-slate-700 p-6 space-y-4">
          {/* Overall progress */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-300 font-medium">
                {isCompleted ? 'Pipeline Complete' : isFailed ? 'Pipeline Failed' : `Running: ${status.current_stage}`}
              </span>
              <span className="text-cyan-400 font-mono">{Math.round(progress * 100)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${isCompleted ? 'bg-green-500' : isFailed ? 'bg-red-500' : 'bg-cyan-500'}`}
                style={{width: `${Math.round(progress*100)}%`}}
              />
            </div>
          </div>

          {/* Stage list */}
          <div className="space-y-1.5">
            {status.stages.map((stage, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                {stage.done ? (
                  <CheckCircle className="h-4 w-4 text-green-400 shrink-0" />
                ) : stage.stage_id === status.current_stage ? (
                  <Loader2 className="h-4 w-4 text-cyan-400 animate-spin shrink-0" />
                ) : (
                  <div className="h-4 w-4 rounded-full border border-slate-600 shrink-0" />
                )}
                <span className={stage.done ? 'text-slate-300' : stage.stage_id === status.current_stage ? 'text-cyan-400' : 'text-slate-500'}>
                  {STAGE_LABELS[stage.stage_id] || stage.message}
                </span>
                {stage.done && <span className="ml-auto text-xs text-slate-500">{new Date(stage.timestamp).toLocaleTimeString()}</span>}
              </div>
            ))}
          </div>

          {/* Actions */}
          {isCompleted && simulationId && (
            <div className="flex gap-3 pt-2">
              <Button onClick={() => router.push(`/simulations/${simulationId}/results`)}>
                View Results <ChevronRight className="h-4 w-4" />
              </Button>
              <Button variant="outline" onClick={() => router.push(`/simulations/${simulationId}/comparison`)}>
                SPH vs Delft3D
              </Button>
              <Button variant="ghost" onClick={() => { setStatus(null); setRunning(false); setSimulationId(null); setError(null); }}>
                Reset
              </Button>
            </div>
          )}
          {isFailed && (
            <Button variant="outline" onClick={startDemo}>Retry Demo</Button>
          )}
        </div>
      )}
    </div>
  );
}
""",

"src/components/charts/HydrographChart.tsx": """'use client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, Legend, ResponsiveContainer } from 'recharts';
import type { HydrologyPoint } from '@/types';

export default function HydrographChart({ data }: { data: HydrologyPoint[] }) {
  if (!data?.length) return <div className="text-slate-400 text-center py-8">No hydrological data</div>;
  const maxQ = Math.max(...data.map(d => d.discharge_m3s));
  const breachHour = data.find(d => d.stage === 'BREACH_START')?.hour;
  const peakHour = data.find(d => d.stage === 'PEAK')?.hour;
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-300">Discharge Hydrograph</h3>
        <span className="text-xs text-amber-400 bg-amber-900/30 px-2 py-0.5 rounded">SYNTHETIC DATA — DEMO</span>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{top:5,right:20,left:10,bottom:5}}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="hour" stroke="#94A3B8" label={{value:'Time (hrs)', position:'insideBottom', offset:-3, fill:'#94A3B8', fontSize:11}} />
          <YAxis stroke="#94A3B8" label={{value:'Q (m³/s)', angle:-90, position:'insideLeft', fill:'#94A3B8', fontSize:11}} />
          <Tooltip contentStyle={{background:'#0F172A',border:'1px solid #334155',borderRadius:'6px',color:'#E2E8F0'}} formatter={(v: number) => [`${v.toFixed(0)} m³/s`, 'Discharge']} labelFormatter={l => `Hour ${l}`} />
          <Legend />
          {breachHour !== undefined && <ReferenceLine x={breachHour} stroke="#F97316" strokeDasharray="4 2" label={{value:'Breach',fill:'#F97316',fontSize:10}} />}
          {peakHour !== undefined && <ReferenceLine x={peakHour} stroke="#EF4444" strokeDasharray="4 2" label={{value:'Peak',fill:'#EF4444',fontSize:10}} />}
          <Line dataKey="discharge_m3s" name="Discharge (m³/s)" stroke="#06B6D4" dot={false} strokeWidth={2.5} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
""",

"src/components/results/FloodResultCard.tsx": """import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import type { FloodResult } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function FloodResultCard({ result, model }: { result: FloodResult; model: 'SPH' | 'DELFT3D' }) {
  if (!result) return null;
  const metrics = [
    { label: 'Max Depth', value: `${result.max_depth_m?.toFixed(1)} m`, icon: '🌊' },
    { label: 'Avg Depth', value: `${result.avg_depth_m?.toFixed(1)} m`, icon: '📊' },
    { label: 'Max Velocity', value: `${result.max_velocity_ms?.toFixed(1)} m/s`, icon: '⚡' },
    { label: 'Inundation Area', value: `${result.inundation_area_km2?.toFixed(1)} km²`, icon: '🗺️' },
    { label: 'Peak Discharge', value: `${result.peak_discharge_m3s?.toFixed(0)} m³/s`, icon: '💧' },
    { label: 'Arrival Time', value: `${result.arrival_time_hrs?.toFixed(1)} hrs`, icon: '⏱️' },
  ];
  const exports = [
    { label: 'GeoJSON', key: 'flood_extent', ext: '.geojson' },
    { label: 'GeoTIFF Depth', key: 'flood_depth', ext: '.tif' },
    { label: 'GeoTIFF Velocity', key: 'velocity', ext: '.tif' },
    { label: 'GeoTIFF Arrival Time', key: 'arrival_time', ext: '.tif' },
    { label: 'Discharge CSV', key: 'discharge', ext: '.csv' },
  ];
  return (
    <Card className={`border-${model==='SPH'?'violet':'blue'}-700/40`}>
      <CardHeader>
        <div className="flex items-center gap-2">
          <CardTitle>{model}</CardTitle>
          <Badge variant="mock">MOCK</Badge>
          <Badge variant="demo">DEMO</Badge>
        </div>
        <p className="text-xs text-amber-400 mt-1">{result.disclaimer}</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 mb-4">
          {metrics.map(m => (
            <div key={m.label} className="bg-slate-800 rounded-lg p-3">
              <div className="text-xs text-slate-400">{m.icon} {m.label}</div>
              <div className="text-lg font-bold text-white mt-1">{m.value || '—'}</div>
            </div>
          ))}
        </div>
        <div className="space-y-1">
          <div className="text-xs text-slate-400 mb-2 font-medium">EXPORTS</div>
          {exports.map(e => {
            const path = result.file_paths?.[e.key];
            return (
              <div key={e.key} className="flex items-center justify-between text-sm">
                <span className="text-slate-400">{e.label}</span>
                {path ? (
                  <a href={`${API_BASE}/api/exports/download?path=${encodeURIComponent(path)}`}
                    className="text-cyan-400 hover:text-cyan-300 text-xs flex items-center gap-1" download>
                    ↓ Download
                  </a>
                ) : <span className="text-slate-600 text-xs">Not available</span>}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
""",

"src/components/results/ComparisonTable.tsx": """import type { ModelComparison } from '@/types';
import { Badge } from '@/components/ui/badge';

const METRIC_LABELS: Record<string, { label: string; unit: string }> = {
  inundation_area_km2: { label: 'Inundation Area', unit: 'km²' },
  max_depth_m: { label: 'Max Depth', unit: 'm' },
  avg_depth_m: { label: 'Avg Depth', unit: 'm' },
  max_velocity_ms: { label: 'Max Velocity', unit: 'm/s' },
  peak_discharge_m3s: { label: 'Peak Discharge', unit: 'm³/s' },
  arrival_time_hrs: { label: 'Arrival Time', unit: 'hrs' },
  affected_population: { label: 'Affected Population', unit: 'people' },
};

export default function ComparisonTable({ comparison }: { comparison: ModelComparison }) {
  if (!comparison) return null;
  return (
    <div className="overflow-x-auto">
      <div className="flex items-center gap-2 mb-3">
        <h3 className="font-medium text-white">SPH vs Delft3D Comparison</h3>
        <Badge variant="mock">MOCK MODELS</Badge>
      </div>
      <p className="text-xs text-amber-400 mb-4">{comparison.disclaimer}</p>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="text-left py-2 pr-4 text-slate-400 font-medium">Metric</th>
            <th className="text-right py-2 px-4 text-violet-400 font-medium">SPH <Badge variant="mock" className="ml-1">MOCK</Badge></th>
            <th className="text-right py-2 px-4 text-blue-400 font-medium">Delft3D <Badge variant="mock" className="ml-1">MOCK</Badge></th>
            <th className="text-right py-2 px-4 text-slate-400 font-medium">Diff</th>
            <th className="text-right py-2 pl-4 text-slate-400 font-medium">%Diff</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(comparison.metrics || {}).map(([key, m]) => {
            const meta = METRIC_LABELS[key] || { label: key, unit: '' };
            const diff = m.difference;
            const diffColor = diff > 0 ? 'text-red-400' : diff < 0 ? 'text-green-400' : 'text-slate-400';
            return (
              <tr key={key} className="border-b border-slate-800 hover:bg-slate-800/50">
                <td className="py-2 pr-4 text-slate-300">{meta.label} <span className="text-slate-500 text-xs">{meta.unit}</span></td>
                <td className="text-right py-2 px-4 text-violet-300 font-mono">{(m.sph ?? 0).toFixed(m.sph > 100 ? 0 : 1)}</td>
                <td className="text-right py-2 px-4 text-blue-300 font-mono">{(m.delft3d ?? 0).toFixed(m.delft3d > 100 ? 0 : 1)}</td>
                <td className={`text-right py-2 px-4 font-mono ${diffColor}`}>{diff > 0 ? '+' : ''}{(diff ?? 0).toFixed(1)}</td>
                <td className={`text-right py-2 pl-4 font-mono ${diffColor}`}>{m.pct_difference > 0 ? '+' : ''}{(m.pct_difference ?? 0).toFixed(1)}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
""",

"src/components/results/ImpactCard.tsx": """import type { ImpactResult } from '@/types';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';

export default function ImpactCard({ impact, model }: { impact: ImpactResult; model: string }) {
  if (!impact) return null;
  const metrics = [
    { label: 'Affected Population', value: (impact.affected_population || 0).toLocaleString(), icon: '👥' },
    { label: 'Villages', value: impact.affected_villages || 0, icon: '🏘️' },
    { label: 'Buildings', value: (impact.affected_buildings || 0).toLocaleString(), icon: '🏠' },
    { label: 'Roads (km)', value: `${(impact.affected_roads_km || 0).toFixed(1)} km`, icon: '🛣️' },
    { label: 'Bridges', value: impact.affected_bridges || 0, icon: '🌉' },
    { label: 'Agriculture (ha)', value: `${(impact.affected_agriculture_ha || 0).toFixed(0)} ha`, icon: '🌾' },
  ];
  const CATEGORY_COLORS: Record<string, string> = { LOW: '#4CAF50', MODERATE: '#FFB300', HIGH: '#F57C00', VERY_HIGH: '#D32F2F' };
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <CardTitle>Impact Analysis — {model}</CardTitle>
          <Badge variant="warning">PRELIMINARY</Badge>
        </div>
        <div className="flex items-start gap-2 text-xs text-amber-400 mt-1">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0 mt-0.5" />
          <span>{impact.disclaimer || 'PRELIMINARY DEMONSTRATION ESTIMATE — Not for real emergency decisions.'}</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-2 mb-4">
          {metrics.map(m => (
            <div key={m.label} className="bg-slate-800 rounded p-3">
              <div className="text-xs text-slate-400">{m.icon} {m.label}</div>
              <div className="text-xl font-bold text-white mt-0.5">{m.value}</div>
            </div>
          ))}
        </div>
        <div className="space-y-2">
          <div className="text-xs text-slate-400 font-medium">Impact Categories</div>
          {Object.entries(impact.impact_categories || {}).map(([cat, data]) => data.applicable ? (
            <div key={cat} className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-sm" style={{background: CATEGORY_COLORS[cat]}} />
              <span className="text-sm text-slate-300">{cat}</span>
              <div className="flex-1 h-1.5 bg-slate-800 rounded-full">
                <div className="h-full rounded-full" style={{width:`${(data.area_fraction||0)*100}%`,background:CATEGORY_COLORS[cat]}} />
              </div>
              <span className="text-xs text-slate-500">{data.estimated_area_km2?.toFixed(1)} km²</span>
            </div>
          ) : null)}
        </div>
      </CardContent>
    </Card>
  );
}
""",

"src/components/pipeline/PipelineProgress.tsx": """import type { SimulationJobStatus } from '@/types';
import { CheckCircle, XCircle, Loader2, Circle } from 'lucide-react';

const STAGES = [
  { id: 'VALIDATING', label: '01 — Data Validation' },
  { id: 'PREPROCESSING', label: '02 — GIS Preprocessing' },
  { id: 'GENERATING_INPUT', label: '03 — Model Input Generation' },
  { id: 'SPH_RUNNING', label: '04 — Mock SPH Simulation' },
  { id: 'DELFT3D_RUNNING', label: '05 — Mock Delft3D Simulation' },
  { id: 'POSTPROCESSING', label: '06 — Post-Processing' },
  { id: 'IMPACT_ANALYSIS', label: '07 — Impact Analysis' },
  { id: 'EXPORTING', label: '08 — GIS Export' },
  { id: 'COMPLETED', label: '09 — Complete' },
];

export default function PipelineProgress({ job }: { job: SimulationJobStatus | null }) {
  if (!job) return <div className="text-slate-500 text-sm">No simulation running</div>;
  const completedIds = new Set(job.stages.filter(s => s.done).map(s => s.stage_id));
  return (
    <div className="space-y-3">
      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span className="text-slate-300">Overall Progress</span>
          <span className="text-cyan-400 font-mono">{Math.round((job.progress||0)*100)}%</span>
        </div>
        <div className="h-2 bg-slate-800 rounded-full">
          <div className={`h-full rounded-full transition-all ${
            job.status === 'COMPLETED' ? 'bg-green-500' : job.status === 'FAILED' ? 'bg-red-500' : 'bg-cyan-500'
          }`} style={{width:`${Math.round((job.progress||0)*100)}%`}} />
        </div>
      </div>
      <div className="space-y-1">
        {STAGES.map(stage => {
          const done = completedIds.has(stage.id);
          const active = job.current_stage === stage.id && !done;
          const failed = job.status === 'FAILED' && active;
          return (
            <div key={stage.id} className={`flex items-center gap-3 px-3 py-1.5 rounded text-sm ${
              done ? 'bg-green-900/20' : active ? 'bg-cyan-900/20' : 'bg-transparent'
            }`}>
              {failed ? <XCircle className="h-4 w-4 text-red-400" /> :
               done ? <CheckCircle className="h-4 w-4 text-green-400" /> :
               active ? <Loader2 className="h-4 w-4 text-cyan-400 animate-spin" /> :
               <Circle className="h-4 w-4 text-slate-600" />}
              <span className={done ? 'text-slate-300' : active ? 'text-cyan-300' : 'text-slate-500'}>
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
""",

"src/components/providers/QueryProvider.tsx": """'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
export default function QueryProvider({ children }: { children: React.ReactNode }) {
  const [qc] = useState(() => new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 30_000 } } }));
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}
""",

"src/hooks/useSimulation.ts": """import { useState, useEffect, useRef } from 'react';
import { getSimulationStatus } from '@/lib/api';
import type { SimulationJobStatus } from '@/types';

export function useSimulation(simulationId: string | null) {
  const [status, setStatus] = useState<SimulationJobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!simulationId) return;
    const poll = async () => {
      try {
        const res = await getSimulationStatus(simulationId);
        const s: SimulationJobStatus = res.data;
        setStatus(s);
        if (s.status !== 'COMPLETED' && s.status !== 'FAILED') {
          pollRef.current = setTimeout(poll, 2000);
        }
      } catch (e: any) {
        setError(e?.message || 'Poll failed');
      }
    };
    poll();
    return () => { if (pollRef.current) clearTimeout(pollRef.current); };
  }, [simulationId]);

  return {
    status,
    error,
    isRunning: status ? !['COMPLETED', 'FAILED', 'CREATED'].includes(status.status) : false,
    isCompleted: status?.status === 'COMPLETED',
    isFailed: status?.status === 'FAILED',
    progress: status?.progress || 0,
    currentStage: status?.current_stage || '',
    stages: status?.stages || [],
  };
}
""",

"src/app/layout.tsx": """import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/layout/Navbar';
import DemoBanner from '@/components/layout/DemoBanner';
import QueryProvider from '@/components/providers/QueryProvider';

const inter = Inter({ subsets: ['latin'] });

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
""",

"src/app/globals.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 188 94% 42%;
  --primary-foreground: 0 0% 100%;
  --card: 222.2 84% 8%;
  --card-foreground: 210 40% 98%;
  --border: 217.2 32.6% 17.5%;
  --ring: 188 94% 42%;
}

@layer base {
  * { @apply border-border; }
  body { @apply bg-slate-950 text-slate-100; }
}

@layer components {
  .demo-badge { @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-900/40 text-amber-300 border border-amber-700/40; }
  .mock-badge { @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-violet-900/40 text-violet-300 border border-violet-700/40; }
  .map-container { @apply w-full h-full; }
}

/* maplibre-gl CSS */
@import 'maplibre-gl/dist/maplibre-gl.css';
""",

"src/app/page.tsx": """'use client';
import { useState, useEffect, Suspense } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { Play, Activity, Waves, AlertTriangle, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getDemoFull, getDemoRiver, getDemoReservoir, getDemoSettlements, getDemoRoads, getDemoDam } from '@/lib/api';

const FloodMap = dynamic(() => import('@/components/map/FloodMap'), { ssr: false, loading: () => <div className="bg-slate-900 animate-pulse w-full h-full" /> });

export default function Dashboard() {
  const [demoData, setDemoData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDemoDam(), getDemoRiver(), getDemoReservoir(), getDemoSettlements(), getDemoRoads()])
      .then(([dam, river, res, settlements, roads]) => {
        setDemoData({ dam: dam.data, river: river.data, reservoir: res.data, settlements: settlements.data, roads: roads.data });
      })
      .catch(() => setDemoData(null))
      .finally(() => setLoading(false));
  }, []);

  const statsCards = [
    { label: 'Scenario', value: 'DAM BREAK', icon: '🏔️', badge: 'DEMO' },
    { label: 'Max Inundation', value: '42.5 km²', icon: '🌊', badge: 'MOCK' },
    { label: 'Max Depth', value: '14.2 m', icon: '📏', badge: 'MOCK' },
    { label: 'Affected Pop.', value: '5,220', icon: '👥', badge: 'PRELIMINARY' },
    { label: 'Peak Discharge', value: '7,050 m³/s', icon: '💧', badge: 'MOCK' },
    { label: 'Arrival Time', value: '0.4 hrs', icon: '⏱️', badge: 'MOCK' },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-56px)] overflow-hidden">
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 shrink-0">
        <div className="flex items-center gap-3">
          <Waves className="h-5 w-5 text-cyan-400" />
          <h1 className="font-semibold text-white">HADR Flood Simulation Platform</h1>
          <Badge variant="demo">SYNTHETIC DEMO</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/demo">
            <Button size="sm" className="gap-2">
              <Play className="h-4 w-4" fill="currentColor" />
              RUN FULL DEMO
            </Button>
          </Link>
          <Link href="/simulations/new">
            <Button size="sm" variant="outline">New Simulation</Button>
          </Link>
        </div>
      </div>

      {/* Main content: Map + sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar */}
        <div className="w-72 shrink-0 border-r border-slate-800 overflow-y-auto p-4 space-y-4">
          {/* Study area */}
          <div>
            <h2 className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Study Area</h2>
            <div className="bg-slate-900 rounded-lg p-3 space-y-1 text-sm">
              <div className="text-white font-medium">Synthetic Himalayan Tributary</div>
              <div className="text-slate-400 text-xs">30.2–30.4°N, 79.8–80.1°E</div>
              <Badge variant="demo" className="mt-1">SYNTHETIC</Badge>
            </div>
          </div>

          {/* Dam info */}
          {demoData?.dam && (
            <div>
              <h2 className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Dam</h2>
              <div className="bg-slate-900 rounded-lg p-3 space-y-2 text-sm">
                <div className="text-white font-medium">{demoData.dam.name}</div>
                <div className="grid grid-cols-2 gap-1 text-xs">
                  <div className="text-slate-400">Height:</div><div className="text-slate-200">{demoData.dam.height_m}m</div>
                  <div className="text-slate-400">Volume:</div><div className="text-slate-200">{demoData.dam.reservoir_volume_mcm} MCM</div>
                  <div className="text-slate-400">Max WL:</div><div className="text-slate-200">{demoData.dam.max_water_level_m}m</div>
                </div>
                <Badge variant="demo">DEMO DATA</Badge>
              </div>
            </div>
          )}

          {/* Model status */}
          <div>
            <h2 className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Models</h2>
            <div className="space-y-2">
              {[{name:'SPH',color:'violet'},{name:'Delft3D',color:'blue'}].map(m => (
                <div key={m.name} className="bg-slate-900 rounded-lg p-3 flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-white">{m.name}</div>
                    <div className="text-xs text-slate-400">Adapter Ready</div>
                  </div>
                  <Badge variant="mock">MOCK</Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Quick links */}
          <div className="space-y-2">
            <Link href="/demo"><Button variant="outline" size="sm" className="w-full justify-start gap-2"><Play className="h-3.5 w-3.5" />Run Full Demo</Button></Link>
            <Link href="/simulations"><Button variant="ghost" size="sm" className="w-full justify-start gap-2"><Activity className="h-3.5 w-3.5" />Simulations</Button></Link>
          </div>
        </div>

        {/* Map */}
        <div className="flex-1 relative">
          {!loading && demoData ? (
            <FloodMap
              riverGeoJSON={demoData.river}
              damLocation={demoData.dam?.coordinates}
              reservoirGeoJSON={demoData.reservoir}
              settlementsGeoJSON={demoData.settlements}
              roadsGeoJSON={demoData.roads}
            />
          ) : (
            <div className="flex items-center justify-center h-full bg-slate-900">
              <div className="text-center space-y-3">
                <Waves className="h-12 w-12 text-cyan-500 mx-auto animate-pulse" />
                <p className="text-slate-400">{loading ? 'Loading demo data...' : 'Unable to connect to backend. Start the backend server.'}</p>
                {!loading && <Link href="/demo"><Button>Try Demo Mode</Button></Link>}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom metrics bar */}
      <div className="shrink-0 border-t border-slate-800 px-4 py-3">
        <div className="flex items-center gap-4 overflow-x-auto">
          {statsCards.map(s => (
            <div key={s.label} className="shrink-0 bg-slate-900 rounded-lg px-4 py-2 flex items-center gap-3">
              <span className="text-lg">{s.icon}</span>
              <div>
                <div className="text-xs text-slate-400">{s.label}</div>
                <div className="text-sm font-bold text-white">{s.value}</div>
              </div>
              <Badge variant={s.badge === 'MOCK' ? 'mock' : s.badge === 'PRELIMINARY' ? 'warning' : 'demo'} className="text-[10px]">
                {s.badge}
              </Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
""",

"src/app/demo/page.tsx": """'use client';
import DemoRunButton from '@/components/demo/DemoRunButton';

export default function DemoPage() {
  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Run Full Demonstration</h1>
        <p className="text-slate-400">Execute the complete end-to-end pipeline using synthetic data and mock hydraulic models.</p>
      </div>
      <DemoRunButton />
    </div>
  );
}
""",

"src/app/simulations/page.tsx": """'use client';
export default function SimulationsPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">Simulations</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/simulations/new/page.tsx": """'use client';
export default function NewSimulationPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">New Simulation</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/simulations/[id]/page.tsx": """'use client';
export default function SimulationPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">Simulation Overview</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/simulations/[id]/results/page.tsx": """'use client';
export default function ResultsPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">Simulation Results</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/simulations/[id]/comparison/page.tsx": """'use client';
export default function ComparisonPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">Model Comparison</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/exports/page.tsx": """'use client';
export default function ExportsPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">Data Exports</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/monitoring/page.tsx": """'use client';
export default function MonitoringPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">Monitoring</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/data/page.tsx": """'use client';
export default function DataPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">Data Management</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/settings/page.tsx": """'use client';
export default function SettingsPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">Settings</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"src/app/about/page.tsx": """'use client';
export default function AboutPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold text-white mb-4">About</h1><p className="text-slate-400">Coming soon</p></div>;
}
""",

"next.config.js": """/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['maplibre-gl'],
};
module.exports = nextConfig;
""",

".env.local": """NEXT_PUBLIC_API_URL=http://localhost:8000
"""

}

base_dir = "/home/abhijeet-rai/DEV/Sih/frontend/"

for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

print(f"Created {len(files)} files.")
