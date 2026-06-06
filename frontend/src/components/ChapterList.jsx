import { Layers3, Plus } from 'lucide-react';
import { motion } from 'motion/react';
import ChapterCard from './ChapterCard';
import { Alert } from './ui/alert';
import { Button } from './ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

function ChapterList({ chapters, onUpdateChapter, onAddChapter, onRemoveChapter, validation }) {
  const totalCharacters = chapters.reduce((sum, chapter) => sum + chapter.content.length, 0);

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
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline" size="icon" onClick={onAddChapter}>
              <Plus className="h-4 w-4" />
              <span className="sr-only">添加章节</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>添加章节</TooltipContent>
        </Tooltip>
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
