import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, ArrowRight, CheckCircle2, Loader2, Sparkles } from 'lucide-react';
import yaml from 'js-yaml';
import { API_BASE_URL, fetchSchema, generateScript, validateYaml } from './api/scriptApi';
import { checkAuth, logout as apiLogout } from './api/authApi';
import AdminDashboard from './components/AdminDashboard';
import AppHeader from './components/AppHeader';
import ChapterList from './components/ChapterList';
import GenerationOptions from './components/GenerationOptions';
import LoginPage from './components/LoginPage';
import YamlWorkspace from './components/YamlWorkspace';
import SchemaModal from './components/SchemaModal';
import { Button } from './components/ui/button';
import { useToast } from './components/ui/toast';
import { getApiErrorMessage } from './lib/apiError';

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

const defaultOptions = {
  genre: '悬疑',
  style: '短剧',
  target_scene_count: 6,
  language: 'zh-CN',
};

const workflowSteps = [
  { id: 'chapters', title: '章节输入', description: '整理小说原文' },
  { id: 'options', title: '生成选项', description: '设置改编方向' },
  { id: 'generate', title: '确认生成', description: '提交 AI 转换' },
  { id: 'result', title: '完成内容', description: '查看和导出' },
];

function App() {
  const toast = useToast();
  const [authLoading, setAuthLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [chapters, setChapters] = useState(initialChapters);
  const [generationOptions, setGenerationOptions] = useState(defaultOptions);
  const [yamlText, setYamlText] = useState(emptyYaml);
  const [loading, setLoading] = useState(false);
  const [yamlChecking, setYamlChecking] = useState(false);
  const [schemaOpen, setSchemaOpen] = useState(false);
  const [schemaText, setSchemaText] = useState('');
  const [usedMock, setUsedMock] = useState(false);
  const [currentStep, setCurrentStep] = useState('chapters');
  const [currentView, setCurrentView] = useState('workspace');

  useEffect(() => {
    checkAuth()
      .then((data) => {
        if (data.authenticated) {
          setUser(data.user);
          if (data.user?.role !== 'admin') {
            setCurrentView('workspace');
          }
        }
      })
      .catch(() => {
        // 后端不可用时保持未登录
      })
      .finally(() => setAuthLoading(false));
  }, []);

  const handleLogout = async () => {
    try {
      await apiLogout();
    } catch {
      // 即使后端调用失败也清除前端状态
    }
    setUser(null);
    setCurrentView('workspace');
  };

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
      return false;
    }

    setLoading(true);
    try {
      const result = await generateScript(chapters, generationOptions);
      setYamlText(result.yaml);
      setUsedMock(result.used_mock);
      if (result.used_mock) {
        toast.info('未配置 DeepSeek API Key，已返回演示剧本。');
      } else {
        toast.success('剧本 YAML 已生成。');
      }
      return true;
    } catch (error) {
      toast.error(getApiErrorMessage(error, '生成失败，请检查后端服务。'));
      return false;
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAndShowResult = async () => {
    const generated = await handleGenerate();
    if (generated) {
      setCurrentStep('result');
    }
  };

  const handleImportChapters = (parsed) => {
    if (parsed.length === 0) {
      toast.error('文件内容为空或无法解析，请检查文件。');
      return;
    }
    setChapters(parsed);
    toast.success(`已导入 ${parsed.length} 个章节`);
  };

  const handleImportError = (message) => {
    toast.error(message);
  };

  const goToOptions = () => {
    if (validation) {
      toast.warning(validation);
      return;
    }
    setCurrentStep('options');
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
    const dateStr = new Date().toISOString().slice(0, 10);
    link.download = `script-output-${dateStr}.yaml`;
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

  if (authLoading) {
    return (
      <div className="login-shell">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!user) {
    return (
      <LoginPage
        onLoginSuccess={(u) => {
          setUser(u);
          setCurrentView('workspace');
        }}
      />
    );
  }

  const currentStepIndex = workflowSteps.findIndex((step) => step.id === currentStep);
  const totalCharacters = chapters.reduce((sum, chapter) => sum + chapter.content.length, 0);

  return (
    <div className="app-shell">
      <AppHeader
        chapterCount={chapters.length}
        validation={validation}
        apiBaseUrl={API_BASE_URL}
        user={user}
        currentView={currentView}
        onViewChange={setCurrentView}
        onLogout={handleLogout}
      />

      {currentView === 'admin' && user.role === 'admin' ? (
        <AdminDashboard toast={toast} />
      ) : (
      <main className="workflow-shell">
        <section className="workflow-hero">
          <div>
            <p className="workflow-kicker">Script workflow</p>
            <h2>{workflowSteps[currentStepIndex]?.title}</h2>
            <p>{workflowSteps[currentStepIndex]?.description}</p>
          </div>
          <div className="workflow-progress" aria-label="生成流程">
            {workflowSteps.map((step, index) => (
              <button
                key={step.id}
                type="button"
                className={`workflow-step ${
                  index === currentStepIndex ? 'workflow-step-active' : ''
                } ${index < currentStepIndex ? 'workflow-step-done' : ''}`}
                onClick={() => {
                  if (index <= currentStepIndex || currentStep === 'result') {
                    setCurrentStep(step.id);
                  }
                }}
              >
                <span>{index < currentStepIndex ? <CheckCircle2 className="h-4 w-4" /> : index + 1}</span>
                <strong>{step.title}</strong>
              </button>
            ))}
          </div>
        </section>

        {currentStep === 'chapters' && (
          <section className="workflow-stage workflow-stage-wide">
            <ChapterList
              chapters={chapters}
              onUpdateChapter={updateChapter}
              onAddChapter={addChapter}
              onRemoveChapter={removeChapter}
              onImportChapters={handleImportChapters}
              onImportError={handleImportError}
              validation={validation}
            />
            <div className="workflow-actions">
              <Button onClick={goToOptions} disabled={Boolean(validation)}>
                下一步
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </section>
        )}

        {currentStep === 'options' && (
          <section className="workflow-stage">
            <GenerationOptions options={generationOptions} onChange={setGenerationOptions} />
            <div className="workflow-summary-card">
              <h3>输入概览</h3>
              <div>
                <span>{chapters.length} 个章节</span>
                <span>{totalCharacters} 字符</span>
                <span>{generationOptions.target_scene_count || 0} 个目标场景</span>
              </div>
            </div>
            <div className="workflow-actions">
              <Button variant="outline" onClick={() => setCurrentStep('chapters')}>
                <ArrowLeft className="h-4 w-4" />
                返回章节
              </Button>
              <Button onClick={() => setCurrentStep('generate')}>
                下一步
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </section>
        )}

        {currentStep === 'generate' && (
          <section className="workflow-stage">
            <div className="generate-review">
              <div>
                <p className="workflow-kicker">Ready to generate</p>
                <h3>确认生成结构化剧本</h3>
                <p>系统将按当前章节和参数生成 YAML，可在完成页继续编辑、校验、复制或下载。</p>
              </div>
              <div className="review-grid">
                <div>
                  <span>章节</span>
                  <strong>{chapters.length}</strong>
                </div>
                <div>
                  <span>类型</span>
                  <strong>{generationOptions.genre || '未设置'}</strong>
                </div>
                <div>
                  <span>风格</span>
                  <strong>{generationOptions.style || '未设置'}</strong>
                </div>
                <div>
                  <span>场景</span>
                  <strong>{generationOptions.target_scene_count || 0}</strong>
                </div>
              </div>
            </div>
            <div className="workflow-actions">
              <Button variant="outline" onClick={() => setCurrentStep('options')}>
                <ArrowLeft className="h-4 w-4" />
                返回选项
              </Button>
              <Button loading={loading} onClick={handleGenerateAndShowResult}>
                <Sparkles className="h-4 w-4" />
                生成并查看结果
              </Button>
            </div>
          </section>
        )}

        {currentStep === 'result' && (
          <section className="workflow-stage workflow-stage-result">
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
              showGenerate={false}
            />
            <div className="workflow-actions">
              <Button variant="outline" onClick={() => setCurrentStep('generate')}>
                <ArrowLeft className="h-4 w-4" />
                返回生成
              </Button>
              <Button loading={loading} onClick={handleGenerateAndShowResult}>
                <Sparkles className="h-4 w-4" />
                重新生成
              </Button>
            </div>
          </section>
        )}
      </main>
      )}

      <SchemaModal
        open={schemaOpen}
        schemaText={schemaText}
        onClose={() => setSchemaOpen(false)}
      />
    </div>
  );
}

export default App;
