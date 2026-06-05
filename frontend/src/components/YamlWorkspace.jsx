import { Alert, Button, Space, Tooltip, Typography } from 'antd';
import {
  CopyOutlined,
  DownloadOutlined,
  FileTextOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import Editor from '@monaco-editor/react';

const { Text, Title } = Typography;

function YamlWorkspace({
  yamlText,
  onYamlChange,
  loading,
  yamlChecking,
  usedMock,
  onGenerate,
  onCopy,
  onDownload,
  onFormatCheck,
  onSchema,
}) {
  return (
    <section className="panel output-panel">
      <div className="panel-heading">
        <div>
          <Title level={4}>剧本 YAML</Title>
          <Text type="secondary">可直接编辑、复制或下载为 .yaml 文件。</Text>
        </div>
        <Space wrap>
          <Tooltip title="生成剧本">
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              loading={loading}
              onClick={onGenerate}
            >
              生成
            </Button>
          </Tooltip>
          <Tooltip title="校验 YAML">
            <Button icon={<ReloadOutlined />} loading={yamlChecking} onClick={onFormatCheck} />
          </Tooltip>
          <Tooltip title="复制">
            <Button icon={<CopyOutlined />} onClick={onCopy} />
          </Tooltip>
          <Tooltip title="下载">
            <Button icon={<DownloadOutlined />} onClick={onDownload} />
          </Tooltip>
          <Tooltip title="查看 JSON Schema">
            <Button icon={<FileTextOutlined />} onClick={onSchema} />
          </Tooltip>
        </Space>
      </div>

      {usedMock && (
        <Alert
          type="info"
          showIcon
          message="当前使用演示输出。配置后端 DeepSeek API Key 后，将根据输入章节实时生成。"
        />
      )}

      <div className="editor-frame">
        <Editor
          height="100%"
          language="yaml"
          value={yamlText}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            wordWrap: 'on',
            scrollBeyondLastLine: false,
            lineNumbersMinChars: 3,
          }}
          onChange={(value) => onYamlChange(value || '')}
        />
      </div>
    </section>
  );
}

export default YamlWorkspace;
