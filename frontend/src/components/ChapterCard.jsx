import { Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

function ChapterCard({ chapter, index, onUpdate, onRemove, disableRemove }) {
  return (
    <Card>
      <CardHeader>
        <Input
          value={chapter.title}
          onChange={(event) => onUpdate(index, 'title', event.target.value)}
          placeholder="章节标题"
          className="border-0 px-0 text-sm font-medium shadow-none focus-visible:ring-0"
        />
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
          className="max-h-56 min-h-32 resize-y"
        />
        <p className="mt-1 text-right text-xs text-muted-foreground">{chapter.content.length} 字符</p>
      </CardContent>
    </Card>
  );
}

export default ChapterCard;
