import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, message, Card, Progress, Spin, Alert, Descriptions, Tag, Collapse, Button } from 'antd';
import { InboxOutlined, CheckCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { uploadExcel } from '../services/api';

const { Dragger } = Upload;
const { Panel } = Collapse;

const UploadPage = ({ onUploadSuccess }) => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setUploading(true);
    setUploadProgress(0);
    setUploadResult(null);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const result = await uploadExcel(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      if (result.success) {
        message.success('ファイルのアップロードと解析が成功しました！');
        setUploadResult(result);
        setError(null);
        // 正常時: 親へ通知して Dashboard へ遷移
        if (onUploadSuccess) {
          try { onUploadSuccess(result.version); } catch (e) { /* noop */ }
        }
        // 少し待ってからリダイレクト（UI 反応演出）
        setTimeout(() => navigate('/dashboard'), 500);
      } else {
        message.error('アップロード失敗');
        setError('バックエンドが success=false を返却しました');
      }
    } catch (error) {
      message.error(`アップロードエラー: ${error.message}`);
      console.error('Upload error:', error);
      setError(error.message);
    } finally {
      setUploading(false);
    }

    return false; // Prevent default upload
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls',
    beforeUpload: handleUpload,
    showUploadList: false,
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card title="📊 Excelデータアップロード" style={{ marginBottom: 24 }}>
        <Dragger {...uploadProps} disabled={uploading}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">クリックまたはドラッグしてファイルをアップロード</p>
          <p className="ant-upload-hint">
            .xlsx または .xls ファイルをサポート（最大100MB）
          </p>
        </Dragger>

        {uploading && (
          <div style={{ marginTop: 24 }}>
            <Spin size="large" />
            <Progress percent={uploadProgress} status="active" style={{ marginTop: 16 }} />
            <p style={{ textAlign: 'center', marginTop: 8 }}>
              ファイルを解析中... しばらくお待ちください
            </p>
          </div>
        )}
      </Card>

      {error && (
        <Card style={{ marginBottom: 24 }} title={<><WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />アップロードエラー</>}>
          <Alert type="error" message="アップロードに失敗しました" description={error} showIcon />
          <Button style={{ marginTop: 16 }} onClick={() => { setError(null); setUploadResult(null); }}>再試行</Button>
        </Card>
      )}

      {uploadResult && !error && (
        <>
          <Card 
            title={<><CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />解析完了 / 自動訓練を開始しています。ダッシュボードへ遷移します...</>}
            style={{ marginBottom: 24 }}
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="バージョン">{uploadResult.version}</Descriptions.Item>
              <Descriptions.Item label="ファイル名">{uploadResult.metadata.filename}</Descriptions.Item>
              <Descriptions.Item label="アップロード時刻">{uploadResult.metadata.timestamp}</Descriptions.Item>
              <Descriptions.Item label="検出シート数">
                {uploadResult.metadata.available_sheets.length}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: 16 }}>
              <strong>利用可能なシート:</strong>
              <div style={{ marginTop: 8 }}>
                {uploadResult.metadata.available_sheets.map((sheet) => (
                  <Tag color="blue" key={sheet} style={{ margin: 4 }}>
                    {sheet}
                  </Tag>
                ))}
              </div>
            </div>
          </Card>

          {uploadResult.warnings && uploadResult.warnings.length > 0 && (
            <Card 
              title={<><WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />警告</>}
              style={{ marginBottom: 24 }}
            >
              {uploadResult.warnings.map((warning, index) => (
                <Alert
                  key={index}
                  message={warning.message}
                  description={warning.impact}
                  type="warning"
                  showIcon
                  style={{ marginBottom: 8 }}
                />
              ))}
            </Card>
          )}

          <Card title="📋 データ詳細">
            <Collapse>
              <Panel header="解析レポート" key="1">
                <pre style={{ maxHeight: 300, overflow: 'auto', backgroundColor: '#f5f5f5', padding: 16 }}>
                  {JSON.stringify(uploadResult.parse_report, null, 2)}
                </pre>
              </Panel>
              <Panel header="質量レポート" key="2">
                <pre style={{ maxHeight: 300, overflow: 'auto', backgroundColor: '#f5f5f5', padding: 16 }}>
                  {JSON.stringify(uploadResult.quality_report, null, 2)}
                </pre>
              </Panel>
              <Panel header="バリデーション結果" key="3">
                <pre style={{ maxHeight: 300, overflow: 'auto', backgroundColor: '#f5f5f5', padding: 16 }}>
                  {JSON.stringify(uploadResult.validation_result, null, 2)}
                </pre>
              </Panel>
              <Panel header="警告 JSON" key="4">
                <pre style={{ maxHeight: 200, overflow: 'auto', backgroundColor: '#fff7e6', padding: 16 }}>
                  {JSON.stringify(uploadResult.warnings, null, 2)}
                </pre>
              </Panel>
            </Collapse>
          </Card>
        </>
      )}
    </div>
  );
};

export default UploadPage;
