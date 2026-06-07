import { BookOpenText, LayoutDashboard, LogOut, PenLine, Server, UserCircle } from 'lucide-react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

function AppHeader({ chapterCount, validation, apiBaseUrl, user, currentView, onViewChange, onLogout }) {
  return (
    <header className="topbar">
      <div className="brand-lockup">
        <div className="brand-mark">
          <BookOpenText className="h-5 w-5" />
        </div>
        <div>
          <h1 className="brand">Novel2Script</h1>
          <p className="subtitle">AI 小说转结构化剧本 YAML 工具</p>
        </div>
      </div>
      <div className="status-cluster">
        <Badge variant={validation ? 'warning' : 'success'}>{chapterCount} 个章节</Badge>
        <Badge variant="secondary" className="gap-1.5">
          <Server className="h-3.5 w-3.5" />
          API {apiBaseUrl.replace(/^https?:\/\//, '')}
        </Badge>
        {user && (
          <>
            <span className="user-pill">
              <UserCircle className="h-3.5 w-3.5" />
              {user.username}
            </span>
            {user.role === 'admin' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onViewChange(currentView === 'admin' ? 'workspace' : 'admin')}
              >
                {currentView === 'admin' ? (
                  <PenLine className="h-3.5 w-3.5" />
                ) : (
                  <LayoutDashboard className="h-3.5 w-3.5" />
                )}
                {currentView === 'admin' ? '返回工作台' : '管理后台'}
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={onLogout}>
              <LogOut className="h-3.5 w-3.5" />
              退出
            </Button>
          </>
        )}
      </div>
    </header>
  );
}

export default AppHeader;
