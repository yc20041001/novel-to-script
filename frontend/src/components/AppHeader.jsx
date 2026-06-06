import { LogOut } from 'lucide-react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

function AppHeader({ chapterCount, validation, apiBaseUrl, user, onLogout }) {
  return (
    <header className="topbar">
      <div>
        <h1 className="brand">Novel2Script</h1>
        <p className="subtitle">AI 小说转结构化剧本 YAML 工具</p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={validation ? 'warning' : 'success'}>{chapterCount} 个章节</Badge>
        <Badge variant="secondary">API: {apiBaseUrl}</Badge>
        {user && (
          <>
            <Badge variant="default">{user.username}</Badge>
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
