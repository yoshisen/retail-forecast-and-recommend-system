import React from 'react';
import { Alert, Button } from 'antd';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // You could send this to logging backend
    // console.error('Boundary caught', error, info);
  }

  handleReload = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) this.props.onReset();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24 }}>
          <Alert
            type="error"
            showIcon
            message="表示エラーが発生しました"
            description={this.state.error?.message || '不明なエラー'}
          />
          <Button style={{ marginTop: 16 }} onClick={this.handleReload}>再読み込み</Button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
