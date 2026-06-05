import { Badge } from './ui/badge';

function AppHeader({ chapterCount, validation, apiBaseUrl }) {
  return (
    <header className="topbar">
      <div>
        <h1 className="brand">Novel2Script</h1>
        <p className="subtitle">AI 小说转结构化剧本 YAML 工具</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <Badge variant={validation ? 'warning' : 'success'}>{chapterCount} 个章节</Badge>
        <Badge variant="secondary">API: {apiBaseUrl}</Badge>
      </div>
    </header>
  );
}

export default AppHeader;
