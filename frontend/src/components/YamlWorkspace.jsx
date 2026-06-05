import { Copy, Download, FileText, RefreshCw, Sparkles } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { Alert } from './ui/alert';
import { Button } from './ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

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
          <h2 className="panel-title">剧本 YAML</h2>
          <p className="panel-description">可直接编辑、复制或下载为 .yaml 文件。</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button loading={loading} onClick={onGenerate}>
                <Sparkles className="h-4 w-4" />
                生成
              </Button>
            </TooltipTrigger>
            <TooltipContent>生成剧本</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" loading={yamlChecking} onClick={onFormatCheck}>
                {!yamlChecking && <RefreshCw className="h-4 w-4" />}
                <span className="sr-only">校验 YAML</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>校验 YAML</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={onCopy}>
                <Copy className="h-4 w-4" />
                <span className="sr-only">复制</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>复制</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={onDownload}>
                <Download className="h-4 w-4" />
                <span className="sr-only">下载</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>下载</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={onSchema}>
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
