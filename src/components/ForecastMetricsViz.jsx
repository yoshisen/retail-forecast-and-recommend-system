import React from 'react';
import { Card, Row, Col, Tooltip } from 'antd';

// Simple horizontal bar without external chart libs
const Bar = ({ value, max, color }) => {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div style={{ marginBottom: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
        <span>{value.toFixed(4)}</span>
        <span>{pct.toFixed(1)}%</span>
      </div>
      <div style={{ height: 8, background: '#f0f0f0', borderRadius: 4 }}>
        <div style={{ width: pct + '%', height: '100%', background: color, borderRadius: 4 }} />
      </div>
    </div>
  );
};

const ForecastMetricsViz = ({ metrics }) => {
  if (!metrics) return null;
  const { mae, rmse, mape } = metrics;
  // Use rmse as the max reference if larger, otherwise compute max among values
  const maxRef = Math.max(mae || 0, rmse || 0, mape || 0);

  return (
    <Card size="small" title="📐 予測モデル指標" style={{ marginTop: 12 }}>
      <Row gutter={12}>
        <Col span={8}>
          <Tooltip title="Mean Absolute Error (平均絶対誤差)">
            <div>
              <strong>MAE</strong>
              <Bar value={mae} max={maxRef} color="#1890ff" />
            </div>
          </Tooltip>
        </Col>
        <Col span={8}>
          <Tooltip title="Root Mean Squared Error (二乗平均平方根誤差)">
            <div>
              <strong>RMSE</strong>
              <Bar value={rmse} max={maxRef} color="#722ed1" />
            </div>
          </Tooltip>
        </Col>
        <Col span={8}>
          <Tooltip title="Mean Absolute Percentage Error (平均絶対パーセント誤差)">
            <div>
              <strong>MAPE</strong>
              <Bar value={mape} max={maxRef} color="#fa8c16" />
            </div>
          </Tooltip>
        </Col>
      </Row>
      <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
        <span>値が小さいほど精度が高い指標です (MAPE は割合扱い)。</span>
      </div>
    </Card>
  );
};

export default ForecastMetricsViz;
