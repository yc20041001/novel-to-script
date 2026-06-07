import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from './ui/button';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('前端页面渲染失败', error, info);
  }

  render() {
    if (!this.state.error) {
      return this.props.children;
    }

    return (
      <div className="app-error-shell">
        <div className="app-error-card">
          <AlertTriangle className="h-8 w-8 text-amber-600" />
          <div>
            <h1>页面加载失败</h1>
            <p>前端渲染时遇到错误，可以刷新页面或退出后重新登录。</p>
            <code>{this.state.error.message}</code>
          </div>
          <Button onClick={() => window.location.reload()}>刷新页面</Button>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
