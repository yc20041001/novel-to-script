import { CheckCircle2, Code2, Copy, Download, FileText, RefreshCw, Sparkles } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { Alert } from './ui/alert';
import { Button } from './ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

const outputIconButtonClass =
  'border-slate-500/30 bg-white/10 text-slate-100 hover:bg-teal-400/20 hover:text-white';

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
  showGenerate = true,
}) {
  const lineCount = yamlText.split('\n').length;

  return (
    <section className="panel output-panel">
      <div className="panel-heading output-heading">
        <div className="flex items-start gap-3">
          <div className="panel-icon panel-icon-slate">
            <Code2 className="h-4 w-4" />
          </div>
          <div>
            <h2 className="panel-title">剧本 YAML</h2>
            <p className="panel-description">可直接编辑、复制或下载为 .yaml 文件。</p>
          </div>
        </div>
        <div className="output-toolbar">
          {showGenerate && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button loading={loading} onClick={onGenerate}>
                  <Sparkles className="h-4 w-4" />
                  生成
                </Button>
              </TooltipTrigger>
              <TooltipContent>生成剧本</TooltipContent>
            </Tooltip>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                loading={yamlChecking}
                onClick={onFormatCheck}
                className={outputIconButtonClass}
              >
                {!yamlChecking && <RefreshCw className="h-4 w-4" />}
                <span className="sr-only">校验 YAML</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>校验 YAML</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={onCopy} className={outputIconButtonClass}>
                <Copy className="h-4 w-4" />
                <span className="sr-only">复制</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>复制</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={onDownload} className={outputIconButtonClass}>
                <Download className="h-4 w-4" />
                <span className="sr-only">下载</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>下载</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={onSchema} className={outputIconButtonClass}>
                <FileText className="h-4 w-4" />
                <span className="sr-only">查看 JSON Schema</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>查看 JSON Schema</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {usedMock && (
        <Alert>当前使用演示输出。配置后端 DeepSeek API Key 后，将根据输入章节实时生成。</Alert>
      )}
      {!usedMock && (
        <div className="workspace-status">
          <CheckCircle2 className="h-4 w-4 text-teal-600" />
          YAML 工作区已连接后端 Schema 校验
        </div>
      )}

      <div className="editor-frame">
        <div className="editor-topbar">
          <div className="editor-tabs">
            <span className="editor-tab-active">script-output.yaml</span>
            <span>Schema ready</span>
          </div>
          <span className="editor-line-count">{lineCount} 行</span>
        </div>
        <div className="editor-body">
          <Editor
            height="62vh"
            language="yaml"
            value={yamlText}
            theme="vs-dark"
            options={{
              automaticLayout: true,
              minimap: { enabled: false },
              fontSize: 14,
              wordWrap: 'on',
              scrollBeyondLastLine: false,
              lineNumbersMinChars: 3,
              padding: { top: 12, bottom: 12 },
            }}
            onChange={(value) => onYamlChange(value || '')}
          />
        </div>
      </div>
    </section>
  );
}

export default YamlWorkspace;
