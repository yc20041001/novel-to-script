import { Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

function ChapterCard({ chapter, index, onUpdate, onRemove, disableRemove }) {
  return (
    <Card className="chapter-card">
      <CardHeader>
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <span className="chapter-index">{index + 1}</span>
          <Input
            value={chapter.title}
            onChange={(event) => onUpdate(index, 'title', event.target.value)}
            placeholder="章节标题"
            className="chapter-title-input"
          />
        </div>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" disabled={disableRemove} onClick={() => onRemove(index)}>
              <Trash2 className="h-4 w-4 text-red-600" />
              <span className="sr-only">删除章节</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>删除章节</TooltipContent>
        </Tooltip>
      </CardHeader>
      <CardContent>
        <Textarea
          value={chapter.content}
          onChange={(event) => onUpdate(index, 'content', event.target.value)}
          placeholder="粘贴该章节正文"
          className="chapter-textarea"
        />
        <p className="mt-1 text-right text-xs text-muted-foreground">{chapter.content.length} 字符</p>
      </CardContent>
    </Card>
  );
}

export default ChapterCard;
