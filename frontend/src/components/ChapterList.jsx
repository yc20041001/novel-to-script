import { Alert, Button, Tooltip, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import ChapterCard from './ChapterCard';

const { Text, Title } = Typography;

function ChapterList({ chapters, onUpdateChapter, onAddChapter, onRemoveChapter, validation }) {
  return (
    <section className="panel input-panel">
      <div className="panel-heading">
        <div>
          <Title level={4}>小说章节</Title>
          <Text type="secondary">输入至少 3 章，系统会拆分人物、地点、场景和节拍。</Text>
        </div>
        <Tooltip title="添加章节">
          <Button icon={<PlusOutlined />} onClick={onAddChapter} />
        </Tooltip>
      </div>

      {validation && <Alert type="warning" showIcon message={validation} />}

      <div className="chapter-list">
        {chapters.map((chapter, index) => (
          <ChapterCard
            key={`${chapter.title}-${index}`}
            chapter={chapter}
            index={index}
            onUpdate={onUpdateChapter}
            onRemove={onRemoveChapter}
            disableRemove={chapters.length <= 3}
          />
        ))}
      </div>
    </section>
  );
}

export default ChapterList;
