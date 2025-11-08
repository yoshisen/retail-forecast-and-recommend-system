import React from 'react';
import { Card, Row, Col, Tooltip } from 'antd';

const Stat = ({ label, value }) => (
  <div style={{ marginBottom: 8 }}>
    <div style={{ fontSize: 12, color: '#666' }}>{label}</div>
    <div style={{ fontSize: 16, fontWeight: 600 }}>{value}</div>
  </div>
);

const Gauge = ({ pct }) => {
  return (
    <div style={{ marginTop: 8 }}>
      <div style={{ height: 12, background: '#f0f0f0', borderRadius: 6, overflow: 'hidden' }}>
        <div style={{ width: pct + '%', background: '#52c41a', height: '100%' }} />
      </div>
      <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>疎密度 (密度): {pct.toFixed(3)}%</div>
    </div>
  );
};

const RecommenderMatrixViz = ({ matrix }) => {
  if (!matrix) return null;
  const { n_users, n_items, n_interactions } = matrix;
  const totalPossible = (n_users || 0) * (n_items || 0);
  const densityPct = totalPossible > 0 ? (n_interactions / totalPossible) * 100 : 0;

  return (
    <Card size="small" title="🕸️ 推薦インタラクション行列" style={{ marginTop: 12 }}>
      <Row gutter={16}>
        <Col span={6}><Stat label="ユーザー数" value={n_users} /></Col>
        <Col span={6}><Stat label="商品数" value={n_items} /></Col>
        <Col span={6}><Stat label="インタラクション件数" value={n_interactions} /></Col>
        <Col span={6}><Stat label="理論最大組み合わせ" value={totalPossible} /></Col>
      </Row>
      <Tooltip title="行列の疎密度 (観測されているユーザー×商品ペアの割合)">
        <Gauge pct={densityPct} />
      </Tooltip>
      <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
        <span>一般的にレコメンド行列は非常に疎です。密度が低いほどコールドスタートや人気バイアスに注意。</span>
      </div>
    </Card>
  );
};

export default RecommenderMatrixViz;
