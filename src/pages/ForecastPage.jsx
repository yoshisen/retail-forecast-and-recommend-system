import React, { useState } from 'react';
import { Card, Form, Input, InputNumber, Button, message, Spin, Alert, Table } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getForecast } from '../services/api';

const ForecastPage = () => {
  const [loading, setLoading] = useState(false);
  const [forecastResult, setForecastResult] = useState(null);
  const [form] = Form.useForm();

  const handleForecast = async (values) => {
    try {
      setLoading(true);
      const response = await getForecast(
        values.product_id,
        values.store_id,
        values.horizon || 14,
        values.use_baseline || false
      );

      if (response.success) {
        setForecastResult(response.data);
        message.success('予測完了！');
      }
    } catch (error) {
      message.error(`予測エラー: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // チャート用データ整形
  const chartData = forecastResult ? 
    forecastResult.dates.map((date, index) => ({
      date,
      予測値: forecastResult.predictions[index]
    })) : [];

  // テーブル用データ
  const tableData = forecastResult ?
    forecastResult.dates.map((date, index) => ({
      key: index,
      date,
      prediction: forecastResult.predictions[index].toFixed(2)
    })) : [];

  const columns = [
    { title: '日付', dataIndex: 'date', key: 'date' },
    { title: '予測販売数', dataIndex: 'prediction', key: 'prediction', align: 'right' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="📈 販売予測" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleForecast}
        >
          <Form.Item
            label="商品ID"
            name="product_id"
            rules={[{ required: true, message: '商品IDを入力してください' }]}
          >
            <Input placeholder="例: P000001" />
          </Form.Item>

          <Form.Item
            label="店舗ID"
            name="store_id"
            rules={[{ required: true, message: '店舗IDを入力してください' }]}
          >
            <Input placeholder="例: AEON0001" />
          </Form.Item>

          <Form.Item
            label="予測期間（日数）"
            name="horizon"
            initialValue={14}
          >
            <InputNumber min={1} max={90} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} size="large">
              予測実行
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
          <p style={{ marginTop: 16 }}>予測計算中...</p>
        </div>
      )}

      {forecastResult && !loading && (
        <>
          <Card title="📊 予測結果サマリー" style={{ marginBottom: 24 }}>
            <Alert
              message={`予測方法: ${forecastResult.method}`}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <p><strong>商品ID:</strong> {forecastResult.product_id}</p>
            <p><strong>店舗ID:</strong> {forecastResult.store_id}</p>
            <p><strong>予測期間:</strong> {forecastResult.horizon} 日間</p>
            <p><strong>総予測販売数:</strong> {forecastResult.total_forecast.toFixed(2)}</p>
            <p><strong>1日平均予測:</strong> {forecastResult.avg_daily_forecast.toFixed(2)}</p>
          </Card>

          <Card title="📉 予測トレンド" style={{ marginBottom: 24 }}>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="予測値" stroke="#1890ff" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card title="📋 詳細データ">
            <Table 
              dataSource={tableData} 
              columns={columns} 
              pagination={{ pageSize: 10 }}
              size="small"
            />
          </Card>
        </>
      )}
    </div>
  );
};

export default ForecastPage;
