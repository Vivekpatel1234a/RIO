import axios from 'axios';

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

// ---- Real HEC-RAS flood raster pipeline (resources/ four files) ----
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const getFloodMeta = () => api.get('/api/flood/meta');
export const floodStateImageUrl = (state: string) => `${API_BASE}/api/flood/state/${state}/image.png`;
export const getFloodStateGrid = (state: string) => api.get(`/api/flood/state/${state}/grid`);
export const getFloodVideos = () => api.get('/api/flood/videos');
export const floodVideoUrl = (name: string) => `${API_BASE}/api/flood/videos/file/${encodeURIComponent(name)}`;
