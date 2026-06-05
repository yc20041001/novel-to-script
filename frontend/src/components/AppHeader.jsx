import { Tag, Typography } from 'antd';
import { Layout } from 'antd';

const { Header } = Layout;
const { Text, Title } = Typography;

function AppHeader({ chapterCount, validation, apiBaseUrl }) {
  return (
    <Header className="topbar">
      <div>
        <Title level={3} className="brand">
          Novel2Script
        </Title>
        <Text className="subtitle">AI 小说转结构化剧本 YAML 工具</Text>
      </div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <Tag color={validation ? 'orange' : 'green'}>{chapterCount} 个章节</Tag>
        <Tag color="blue">API: {apiBaseUrl}</Tag>
      </div>
    </Header>
  );
}

export default AppHeader;
