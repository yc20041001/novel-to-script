import { useRef } from 'react';
import { FileUp, Layers3, Plus } from 'lucide-react';
import { motion } from 'motion/react';
import { parseNovelFile } from '../lib/parseNovelFile';
import ChapterCard from './ChapterCard';
import { Alert } from './ui/alert';
import { Button } from './ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

function ChapterList({
  chapters,
  onUpdateChapter,
  onAddChapter,
  onRemoveChapter,
  onImportChapters,
  onImportError,
  validation,
}) {
  const totalCharacters = chapters.reduce((sum, chapter) => sum + chapter.content.length, 0);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target?.result;
      if (typeof text !== 'string' || !text.trim()) {
        onImportError?.('文件内容为空，请选择包含小说正文的文件。');
        return;
      }
      const parsed = parseNovelFile(text);
      if (parsed.length > 0) {
        onImportChapters(parsed);
      } else {
        onImportError?.('文件内容无法解析，请检查章节标题或正文内容。');
      }
    };
    reader.onerror = () => {
      onImportError?.('文件读取失败，请重新选择 .txt 或 .md 文件。');
    };
    reader.readAsText(file);
    // 重置 input 以便重复选择同一文件
    e.target.value = '';
  };

  return (
    <section className="panel input-panel">
      <div className="panel-heading">
        <div className="flex items-start gap-3">
          <div className="panel-icon panel-icon-teal">
            <Layers3 className="h-4 w-4" />
          </div>
          <div>
            <h2 className="panel-title">小说章节</h2>
            <p className="panel-description">输入至少 3 章，系统会拆分人物、地点、场景和节拍。</p>
          </div>
        </div>
        <div className="flex gap-1.5">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={() => fileInputRef.current?.click()}>
                <FileUp className="h-4 w-4" />
                <span className="sr-only">导入文件</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>导入 .txt / .md 文件</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={onAddChapter}>
                <Plus className="h-4 w-4" />
                <span className="sr-only">添加章节</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>添加章节</TooltipContent>
          </Tooltip>
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md"
            className="hidden"
            onChange={handleFileSelect}
          />
        </div>
      </div>

      <div className="input-metrics">
        <span>{chapters.length} 个章节</span>
        <span>{totalCharacters} 字符</span>
        <span>{validation ? '待补全' : '可生成'}</span>
      </div>

      {validation && <Alert variant="warning">{validation}</Alert>}

      <div className="chapter-list">
        {chapters.map((chapter, index) => (
          <motion.div
            key={`${chapter.title}-${index}`}
            layout
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.16 }}
          >
            <ChapterCard
              chapter={chapter}
              index={index}
              onUpdate={onUpdateChapter}
              onRemove={onRemoveChapter}
              disableRemove={chapters.length <= 3}
            />
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export default ChapterList;
