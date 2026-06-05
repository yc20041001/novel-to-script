import { Button, Card, Input, Tooltip } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';

function ChapterCard({ chapter, index, onUpdate, onRemove, disableRemove }) {
  return (
    <Card
      size="small"
      title={
        <Input
          value={chapter.title}
          onChange={(event) => onUpdate(index, 'title', event.target.value)}
          placeholder="章节标题"
          variant="borderless"
        />
      }
      extra={
        <Tooltip title="删除章节">
          <Button
            icon={<DeleteOutlined />}
            danger
            disabled={disableRemove}
            onClick={() => onRemove(index)}
          />
        </Tooltip>
      }
    >
      <Input.TextArea
        value={chapter.content}
        onChange={(event) => onUpdate(index, 'content', event.target.value)}
        placeholder="粘贴该章节正文"
        autoSize={{ minRows: 5, maxRows: 9 }}
        showCount
      />
    </Card>
  );
}

export default ChapterCard;
