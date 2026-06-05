import { useMemo, useState } from 'react';
import yaml from 'js-yaml';
import { API_BASE_URL, fetchSchema, generateScript, validateYaml } from './api/scriptApi';
import AppHeader from './components/AppHeader';
import ChapterList from './components/ChapterList';
import YamlWorkspace from './components/YamlWorkspace';
import SchemaModal from './components/SchemaModal';
import { useToast } from './components/ui/toast';

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
  const toast = useToast();
  const [chapters, setChapters] = useState(initialChapters);
  const [yamlText, setYamlText] = useState(emptyYaml);
  const [loading, setLoading] = useState(false);
  const [yamlChecking, setYamlChecking] = useState(false);
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
      toast.warning(validation);
      return;
    }

    setLoading(true);
    try {
      const result = await generateScript(chapters);
      setYamlText(result.yaml);
      setUsedMock(result.used_mock);
      if (result.used_mock) {
        toast.info('未配置 DeepSeek API Key，已返回演示剧本。');
      } else {
        toast.success('剧本 YAML 已生成。');
      }
    } catch (error) {
      toast.error(error?.response?.data?.detail || '生成失败，请检查后端服务。');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(yamlText);
    toast.success('YAML 已复制。');
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

  const handleFormatCheck = async () => {
    // 1) 客户端本地 YAML 语法校验
    try {
      yaml.load(yamlText);
    } catch (error) {
      toast.error(`YAML 格式错误：${error.message}`);
      return;
    }

    // 2) 调用后端校验 Schema
    setYamlChecking(true);
    try {
      const result = await validateYaml(yamlText);
      if (result.valid) {
        toast.success('YAML 已通过 Schema 校验。');
      } else {
        const detail = result.errors?.length ? result.errors.join('；') : '未知 Schema 校验错误';
        toast.error(`YAML 不符合 Schema：${detail}`);
      }
    } catch {
      toast.error('后端 YAML 校验服务不可用，请确认 FastAPI 已启动。');
    } finally {
      setYamlChecking(false);
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
    <div className="app-shell">
      <AppHeader
        chapterCount={chapters.length}
        validation={validation}
        apiBaseUrl={API_BASE_URL}
      />

      <main className="workspace">
        <ChapterList
          chapters={chapters}
          onUpdateChapter={updateChapter}
          onAddChapter={addChapter}
          onRemoveChapter={removeChapter}
          validation={validation}
        />

        <YamlWorkspace
          yamlText={yamlText}
          onYamlChange={setYamlText}
          loading={loading}
          yamlChecking={yamlChecking}
          usedMock={usedMock}
          onGenerate={handleGenerate}
          onCopy={handleCopy}
          onDownload={handleDownload}
          onFormatCheck={handleFormatCheck}
          onSchema={handleSchema}
        />
      </main>

      <SchemaModal
        open={schemaOpen}
        schemaText={schemaText}
        onClose={() => setSchemaOpen(false)}
      />
    </div>
  );
}

export default App;
