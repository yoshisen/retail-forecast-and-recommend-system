import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload Excel file
export const uploadExcel = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 120000, // 2 minutes for large files
  });
  
  return response.data;
};

// Get data summary
export const getDataSummary = async (version = null) => {
  const params = version ? { version } : {};
  const response = await api.get('/data/summary', { params });
  return response.data;
};

// Get quality report
export const getQualityReport = async (version = null) => {
  const params = version ? { version } : {};
  const response = await api.get('/data/quality', { params });
  return response.data;
};

// Get versions list
export const getVersions = async () => {
  const response = await api.get('/versions');
  return response.data;
};

// Train forecast model
export const trainForecastModel = async (version = null) => {
  const params = version ? { version } : {};
  const response = await api.post('/forecast/train', null, { params });
  return response.data;
};

// Get forecast
export const getForecast = async (productId, storeId, horizon = 14, useBaseline = false, version = null) => {
  const params = { product_id: productId, store_id: storeId, horizon, use_baseline: useBaseline };
  if (version) params.version = version;
  
  const response = await api.get('/forecast', { params });
  return response.data;
};

// Batch forecast
export const batchForecast = async (pairs, horizon = 14, version = null) => {
  const params = version ? { version } : {};
  const response = await api.post('/forecast/batch', { pairs, horizon }, { params });
  return response.data;
};

// Train recommender
export const trainRecommender = async (version = null) => {
  const params = version ? { version } : {};
  const response = await api.post('/recommend/train', null, { params });
  return response.data;
};

// Get recommendations
export const getRecommendations = async (customerId, topK = 10, version = null) => {
  const params = { customer_id: customerId, top_k: topK };
  if (version) params.version = version;
  
  const response = await api.get('/recommend', { params });
  return response.data;
};

// Get popular recommendations
export const getPopularRecommendations = async (topK = 10, storeId = null, version = null) => {
  const params = { top_k: topK };
  if (storeId) params.store_id = storeId;
  if (version) params.version = version;
  
  const response = await api.get('/recommend/popular', { params });
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await axios.get('http://localhost:8000/api/health');
  return response.data;
};

export default api;
