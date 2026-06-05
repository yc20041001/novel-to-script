import { useMemo, useState } from 'react';
import Editor from '@monaco-editor/react';
import yaml from 'js-yaml';
import {
  Alert,
  Button,
  Card,
  Divider,
  Input,
  Layout,
  Modal,
  Space,
  Tag,
  Tooltip,
  Typography,
  message,
} from 'antd';
import {
  CopyOutlined,
  DeleteOutlined,
  DownloadOutlined,
  FileTextOutlined,
  PlusOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { API_BASE_URL, fetchSchema, generateScript } from './api/scriptApi';

const { Header, Content } = Layout;
const { Text, Title } = Typography;

const initialChapters = [
  {
    title: '第一章 雨夜',
    content:
      '雨下得很急。林晚抱着一摞退稿走进巷尾的旧书店，门口的铜铃轻轻响了一声。柜台上放着一个没有署名的牛皮纸袋，里面是一份写到一半的手稿。',
  },
  {
    title: '第二章 手稿',
    content:
      '手稿的第一页写着她的名字。林晚以为这是恶作剧，可每一行字都像在描述她刚刚经历过的雨夜。她拨通书店老板的电话，却只听见一阵断断续续的电流声。',
  },
  {
    title: '第三章 旧书店',
    content:
      '楼上传来脚步声。林晚握紧手机，沿着狭窄的木楼梯往上走。二楼没有人，只有一台老式打字机正在自己敲字，纸上缓慢出现一句话：不要相信结局。',
  },
];

const emptyYaml = `metadata:
  title: ""
  genre: ""
  language: "zh-CN"
  version: "1.0"
  logline: ""
source:
  chapter_count: 3
  chapter_titles: []
characters: []
locations: []
scenes: []
notes: []
`;

function App() {
  const [chapters, setChapters] = useState(initialChapters);
  const [yamlText, setYamlText] = useState(emptyYaml);
  const [loading, setLoading] = useState(false);
  const [schemaOpen, setSchemaOpen] = useState(false);
  const [schemaText, setSchemaText] = useState('');
  const [usedMock, setUsedMock] = useState(false);

  const validation = useMemo(() => {
    if (chapters.length < 3) {
      return '请至少保留 3 个章节。';
    }
    const emptyIndex = chapters.findIndex(
      (chapter) => !chapter.title.trim() || !chapter.content.trim(),
    );
    if (emptyIndex >= 0) {
      return `第 ${emptyIndex + 1} 个章节标题或正文为空。`;
    }
    return '';
  }, [chapters]);

  const updateChapter = (index, field, value) => {
    setChapters((current) =>
      current.map((chapter, currentIndex) =>
        currentIndex === index ? { ...chapter, [field]: value } : chapter,
      ),
    );
  };

  const addChapter = () => {
    setChapters((current) => [
      ...current,
      {
        title: `第${current.length + 1}章`,
        content: '',
      },
    ]);
  };

  const removeChapter = (index) => {
    setChapters((current) => current.filter((_, currentIndex) => currentIndex !== index));
  };

  const handleGenerate = async () => {
    if (validation) {
      message.warning(validation);
      return;
    }

    setLoading(true);
    try {
      const result = await generateScript(chapters);
      setYamlText(result.yaml);
      setUsedMock(result.used_mock);
      if (result.used_mock) {
        message.info('未配置 DeepSeek API Key，已返回演示剧本。');
      } else {
        message.success('剧本 YAML 已生成。');
      }
    } catch (error) {
      message.error(error?.response?.data?.detail || '生成失败，请检查后端服务。');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(yamlText);
    message.success('YAML 已复制。');
  };

  const handleDownload = () => {
    const blob = new Blob([yamlText], { type: 'text/yaml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'script-output.yaml';
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleFormatCheck = () => {
    try {
      yaml.load(yamlText);
      message.success('YAML 格式有效。');
    } catch (error) {
      message.error(`YAML 格式错误：${error.message}`);
    }
  };

  const handleSchema = async () => {
    setSchemaOpen(true);
    if (schemaText) {
      return;
    }
    try {
      const schema = await fetchSchema();
      setSchemaText(JSON.stringify(schema, null, 2));
    } catch {
      setSchemaText('无法获取后端 Schema，请确认 FastAPI 服务正在运行。');
    }
  };

  return (
    <Layout className="app-shell">
      <Header className="topbar">
        <div>
          <Title level={3} className="brand">
            Novel2Script
          </Title>
          <Text className="subtitle">AI 小说转结构化剧本 YAML 工具</Text>
        </div>
        <Space wrap>
          <Tag color={validation ? 'orange' : 'green'}>{chapters.length} 个章节</Tag>
          <Tag color="blue">API: {API_BASE_URL}</Tag>
        </Space>
      </Header>

      <Content className="workspace">
        <section className="panel input-panel">
          <div className="panel-heading">
            <div>
              <Title level={4}>小说章节</Title>
              <Text type="secondary">输入至少 3 章，系统会拆分人物、地点、场景和节拍。</Text>
            </div>
            <Tooltip title="添加章节">
              <Button icon={<PlusOutlined />} onClick={addChapter} />
            </Tooltip>
          </div>

          {validation && <Alert type="warning" showIcon message={validation} />}

          <div className="chapter-list">
            {chapters.map((chapter, index) => (
              <Card
                key={`${chapter.title}-${index}`}
                size="small"
                title={
                  <Input
                    value={chapter.title}
                    onChange={(event) => updateChapter(index, 'title', event.target.value)}
                    placeholder="章节标题"
                    variant="borderless"
                  />
                }
                extra={
                  <Tooltip title="删除章节">
                    <Button
                      icon={<DeleteOutlined />}
                      danger
                      disabled={chapters.length <= 3}
                      onClick={() => removeChapter(index)}
                    />
                  </Tooltip>
                }
              >
                <Input.TextArea
                  value={chapter.content}
                  onChange={(event) => updateChapter(index, 'content', event.target.value)}
                  placeholder="粘贴该章节正文"
                  autoSize={{ minRows: 5, maxRows: 9 }}
                  showCount
                />
              </Card>
            ))}
          </div>
        </section>

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
                  onClick={handleGenerate}
                >
                  生成
                </Button>
              </Tooltip>
              <Tooltip title="校验 YAML">
                <Button icon={<ReloadOutlined />} onClick={handleFormatCheck} />
              </Tooltip>
              <Tooltip title="复制">
                <Button icon={<CopyOutlined />} onClick={handleCopy} />
              </Tooltip>
              <Tooltip title="下载">
                <Button icon={<DownloadOutlined />} onClick={handleDownload} />
              </Tooltip>
              <Tooltip title="查看 JSON Schema">
                <Button icon={<FileTextOutlined />} onClick={handleSchema} />
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
              onChange={(value) => setYamlText(value || '')}
            />
          </div>
        </section>
      </Content>

      <Modal
        title="ScriptDocument JSON Schema"
        open={schemaOpen}
        onCancel={() => setSchemaOpen(false)}
        footer={null}
        width={900}
      >
        <Divider />
        <div className="schema-view">
          <Editor
            height="460px"
            language="json"
            value={schemaText}
            theme="vs-dark"
            options={{
              readOnly: true,
              minimap: { enabled: false },
              wordWrap: 'on',
              scrollBeyondLastLine: false,
            }}
          />
        </div>
      </Modal>
    </Layout>
  );
}

export default App;

