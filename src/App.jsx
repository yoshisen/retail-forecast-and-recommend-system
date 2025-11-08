import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import { Layout, Menu, Typography, Tag } from 'antd';
import {
  UploadOutlined,
  DashboardOutlined,
  LineChartOutlined,
  GiftOutlined,
} from '@ant-design/icons';
import UploadPage from './pages/UploadPage';
import Dashboard from './pages/Dashboard';
import ForecastPage from './pages/ForecastPage';
import RecommendPage from './pages/RecommendPage';
import './App.css';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [currentVersion, setCurrentVersion] = useState(null);
  const [selectedKey, setSelectedKey] = useState(location.pathname);

  useEffect(() => {
    setSelectedKey(location.pathname);
  }, [location.pathname]);

  const handleUploadSuccess = (version) => {
    if (typeof version === 'string') {
      setCurrentVersion(version);
    } else if (version && version.version) {
      setCurrentVersion(version.version);
    }
  };

  const menuItems = [
    { key: '/upload', icon: <UploadOutlined />, label: 'データアップロード' },
    { key: '/dashboard', icon: <DashboardOutlined />, label: 'ダッシュボード' },
    { key: '/forecast', icon: <LineChartOutlined />, label: '販売予測' },
    { key: '/recommend', icon: <GiftOutlined />, label: '商品推薦' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: 20,
          fontWeight: 'bold'
        }}>
          {collapsed ? '🛒' : '🛒 METADATAS AI'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{
          padding: '0 24px',
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Title level={3} style={{ margin: 0 }}>
            リテール分析 & ML プラットフォーム
          </Title>
          {currentVersion && (
            <Tag color="blue">バージョン: {currentVersion}</Tag>
          )}
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#f0f2f5' }}>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Navigate to="/upload" replace />} />
              <Route path="/upload" element={<UploadPage onUploadSuccess={handleUploadSuccess} />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/forecast" element={<ForecastPage />} />
              <Route path="/recommend" element={<RecommendPage />} />
            </Routes>
          </ErrorBoundary>
        </Content>
      </Layout>
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <AppShell />
    </Router>
  );
}

export default App;
