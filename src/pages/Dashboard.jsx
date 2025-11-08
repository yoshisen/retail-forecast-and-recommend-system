import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, message, Spin, Alert, Tag, Progress } from 'antd';
import { 
  ShoppingCartOutlined, 
  UserOutlined, 
  ShopOutlined, 
  DatabaseOutlined,
  RocketOutlined,
  GiftOutlined
} from '@ant-design/icons';
import { getDataSummary, trainForecastModel, trainRecommender } from '../services/api';
import ForecastMetricsViz from '../components/ForecastMetricsViz';
import RecommenderMatrixViz from '../components/RecommenderMatrixViz';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [showForecastTrace, setShowForecastTrace] = useState(false);
  const [showRecommendTrace, setShowRecommendTrace] = useState(false);
  const [training, setTraining] = useState({ forecast: false, recommender: false });
  const [polling, setPolling] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    loadSummary();
  }, []);

  // Establish WebSocket for training updates
  useEffect(() => {
    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const wsUrl = base.replace(/^http/, 'ws') + '/ws/training';
    let ws;
    try {
      ws = new WebSocket(wsUrl);
      ws.onopen = () => setWsConnected(true);
      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          if (msg.type === 'training_update') {
            setSummary(prev => {
              if (!prev) return prev; // Not ready yet
              const training = { ...(prev.training || {}) };
              training[msg.model] = msg.status;
              training[`${msg.model}_progress`] = msg.progress;
              if (msg.metrics) training[`${msg.model}_metrics`] = msg.metrics;
              if (msg.error) training[`${msg.model}_error`] = msg.error;
              return { ...prev, training };
            });
          }
        } catch (e) {
          console.error('WS parse error', e);
        }
      };
      ws.onclose = () => {
        setWsConnected(false);
        // fallback polling when disconnected
        setPolling(true);
      };
    } catch (e) {
      console.error('WS init failed', e);
      setWsConnected(false);
      setPolling(true);
    }
    return () => ws && ws.close();
  }, []);

  // Fallback polling when ws disconnected
  useEffect(() => {
    if (!polling) return;
    let interval = setInterval(() => loadSummary(true), 6000);
    return () => clearInterval(interval);
  }, [polling]);

  // Stop polling & hide alert once all training finished (not pending/running)
  useEffect(() => {
    if (!summary) return;
    const ti = summary.training || {};
    const active = ['pending','running'];
    const forecastActive = active.includes(ti.forecast);
    const recommendActive = active.includes(ti.recommend);
    if (polling && !forecastActive && !recommendActive) {
      setPolling(false);
    }
  }, [summary, polling]);

  const loadSummary = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      const response = await getDataSummary();
      if (response.success) {
        setSummary(response.data);
      }
    } catch (error) {
      message.error(`データ読み込みエラー: ${error.message}`);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const handleTrainForecast = async () => {
    try {
      setTraining({ ...training, forecast: true });
      message.info('予測モデル訓練中...');
      
      const response = await trainForecastModel();
      
      if (response.success) {
        message.success('予測モデル訓練完了！');
        loadSummary(true);
      }
    } catch (error) {
      message.error(`訓練エラー: ${error.message}`);
    } finally {
      setTraining({ ...training, forecast: false });
    }
  };

  const handleTrainRecommender = async () => {
    try {
      setTraining({ ...training, recommender: true });
      message.info('推薦モデル訓練中...');
      
      const response = await trainRecommender();
      
      if (response.success) {
        message.success('推薦モデル訓練完了！');
        loadSummary(true);
      }
    } catch (error) {
      message.error(`訓練エラー: ${error.message}`);
    } finally {
      setTraining({ ...training, recommender: false });
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!summary) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          message="データがありません"
          description="先にExcelファイルをアップロードしてください"
          type="warning"
          showIcon
        />
      </div>
    );
  }

  const overallSummary = summary.overall_summary || {};
  const trainingInfo = summary.training || {};

  const statusColor = (s) => {
    switch (s) {
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'pending': return 'gold';
      case 'skipped': return 'default';
      default: return 'blue';
    }
  };

  // 表示用ステータス翻訳
  const translateStatus = (s) => {
    switch (s) {
      case 'pending': return '待機中';
      case 'running': return '実行中';
      case 'failed': return '失敗';
      case 'skipped': return 'スキップ';
      case 'completed': return '完成';
      default: return s || 'N/A';
    }
  };

  const StatusTag = ({ type }) => {
    const st = trainingInfo[type];
    if (!st || st === 'completed') return null; // 完了時は非表示
    return <Tag color={statusColor(st)}>{type}: {translateStatus(st)}</Tag>;
  };

  return (
    <div style={{ padding: 24 }}>
      <Card title="📊 データサマリー" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="総シート数"
                value={overallSummary.total_sheets || 0}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="総レコード数"
                value={overallSummary.total_rows || 0}
                prefix={<ShoppingCartOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="総フィールド数"
                value={overallSummary.total_fields || 0}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="バージョン"
                value={summary.version}
                valueStyle={{ fontSize: 16 }}
              />
            </Card>
          </Col>
        </Row>
      </Card>

      <Card title="📈 シート別データ" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          {Object.entries(summary.sheet_summaries || {}).map(([sheetName, sheetData]) => (
            <Col span={8} key={sheetName} style={{ marginBottom: 16 }}>
              <Card size="small" title={sheetName}>
                <Statistic title="行数" value={sheetData.rows} />
                <Statistic title="列数" value={sheetData.columns} />
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      <Card title="🤖 モデル訓練" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <RocketOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
                <h3>販売予測モデル</h3>
                <p style={{ marginBottom: 4 }}>LightGBM ベース時系列予測</p>
                <p style={{ marginTop: 0 }}>自動訓練: {translateStatus(trainingInfo.forecast)}</p>
                <StatusTag type="forecast" />
                {['pending','running'].includes(trainingInfo.forecast) && (
                  <div style={{ marginTop: 12 }}>
                    <Progress percent={trainingInfo.forecast_progress || 0} status="active" />
                    <small style={{ color: '#888' }}>バックグラウンド訓練中...</small>
                  </div>
                )}
                {trainingInfo.forecast === 'completed' && trainingInfo.forecast_metrics && (
                  <ForecastMetricsViz metrics={trainingInfo.forecast_metrics} />
                )}
                <Button 
                  type="primary" 
                  size="large"
                  loading={training.forecast}
                  onClick={handleTrainForecast}
                  disabled={['pending','running'].includes(trainingInfo.forecast)}
                >
                  訓練開始
                </Button>
                {['failed','skipped','completed'].includes(trainingInfo.forecast) && (
                  <Button style={{ marginLeft: 8 }} onClick={handleTrainForecast} disabled={training.forecast}>
                    再訓練
                  </Button>
                )}
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <GiftOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
                <h3>推薦システム</h3>
                <p style={{ marginBottom: 4 }}>協同フィルタリング + コンテンツベース</p>
                <p style={{ marginTop: 0 }}>自動訓練: {translateStatus(trainingInfo.recommend)}</p>
                <StatusTag type="recommend" />
                {['pending','running'].includes(trainingInfo.recommend) && (
                  <div style={{ marginTop: 12 }}>
                    <Progress percent={trainingInfo.recommend_progress || 0} status="active" />
                    <small style={{ color: '#888' }}>バックグラウンド訓練中...</small>
                  </div>
                )}
                {trainingInfo.recommend === 'completed' && trainingInfo.recommend_matrix_info && (
                  <RecommenderMatrixViz matrix={trainingInfo.recommend_matrix_info} />
                )}
                <Button 
                  type="primary" 
                  size="large"
                  loading={training.recommender}
                  onClick={handleTrainRecommender}
                  style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                  disabled={['pending','running'].includes(trainingInfo.recommend)}
                >
                  訓練開始
                </Button>
                {['failed','skipped','completed'].includes(trainingInfo.recommend) && (
                  <Button style={{ marginLeft: 8 }} onClick={handleTrainRecommender} disabled={training.recommender}>
                    再訓練
                  </Button>
                )}
              </div>
            </Card>
          </Col>
        </Row>
        {polling && (() => {
          const ti = trainingInfo;
          const active = ['pending','running'];
          const anyActive = active.includes(ti.forecast) || active.includes(ti.recommend);
          return anyActive ? (
            <Alert style={{ marginTop: 16 }} type="info" showIcon message="自動訓練進行中" description="状態が完了するまで数秒ごとに更新しています" />
          ) : null;
        })()}
      </Card>

      <Card title="ℹ️ システム情報">
        <p><strong>アップロード日時:</strong> {summary.uploaded_at}</p>
        <p><strong>ファイル名:</strong> {summary.filename}</p>
  <p><strong>自動訓練状態:</strong> 予測: {translateStatus(trainingInfo.forecast)} / 推薦: {translateStatus(trainingInfo.recommend)}</p>
                {trainingInfo.forecast_error && (
                  <div style={{ marginTop: 12 }}>
                    <Alert type="error" showIcon message="予測訓練失敗" description={trainingInfo.forecast_error} />
                    {trainingInfo.forecast_error_trace && (
                      <Button size="small" style={{ marginTop: 8 }} onClick={() => setShowForecastTrace(v => !v)}>
                        {showForecastTrace ? 'ログを隠す' : '詳細ログを見る'}
                      </Button>
                    )}
                    {showForecastTrace && trainingInfo.forecast_error_trace && (
                      <pre style={{
                        marginTop: 8,
                        maxHeight: 240,
                        overflow: 'auto',
                        background: '#1e1e1e',
                        color: '#dcdcdc',
                        padding: 12,
                        borderRadius: 4,
                        fontSize: 12
                      }}>{trainingInfo.forecast_error_trace}</pre>
                    )}
                  </div>
                )}
                {trainingInfo.recommend_error && (
                  <div style={{ marginTop: 12 }}>
                    <Alert type="error" showIcon message="推薦訓練失敗" description={trainingInfo.recommend_error} />
                    {trainingInfo.recommend_error_trace && (
                      <Button size="small" style={{ marginTop: 8 }} onClick={() => setShowRecommendTrace(v => !v)}>
                        {showRecommendTrace ? 'ログを隠す' : '詳細ログを見る'}
                      </Button>
                    )}
                    {showRecommendTrace && trainingInfo.recommend_error_trace && (
                      <pre style={{
                        marginTop: 8,
                        maxHeight: 240,
                        overflow: 'auto',
                        background: '#1e1e1e',
                        color: '#dcdcdc',
                        padding: 12,
                        borderRadius: 4,
                        fontSize: 12
                      }}>{trainingInfo.recommend_error_trace}</pre>
                    )}
                  </div>
                )}
      </Card>
    </div>
  );
};

export default Dashboard;
