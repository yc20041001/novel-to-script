import { SlidersHorizontal } from 'lucide-react';
import { Input } from './ui/input';

const STYLE_SUGGESTIONS = ['短剧', '影视剧', '广播剧', '舞台剧'];
const GENRE_SUGGESTIONS = ['悬疑', '爱情', '奇幻', '剧情', '武侠', '科幻', '喜剧', '惊悚'];

function OptionField({ label, id, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium text-foreground">
        {label}
      </label>
      {children}
    </div>
  );
}

function SuggestionChips({ suggestions, selected, onSelect }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {suggestions.map((item) => (
        <button
          key={item}
          type="button"
          onClick={() => onSelect(item)}
          className={`option-chip ${selected === item ? 'option-chip-active' : 'option-chip-idle'}`}
        >
          {item}
        </button>
      ))}
    </div>
  );
}

function GenerationOptions({ options, onChange }) {
  const update = (field, value) => {
    onChange({ ...options, [field]: value });
  };

  return (
    <div className="options-panel">
      <div className="mb-3 flex items-center gap-2">
        <div className="panel-icon panel-icon-amber">
          <SlidersHorizontal className="h-4 w-4" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground">生成选项</h3>
          <p className="text-xs text-muted-foreground">控制改编方向和输出颗粒度</p>
        </div>
      </div>
      <div className="option-summary">
        <span>{options.genre || '未设置类型'}</span>
        <span>{options.style || '未设置风格'}</span>
        <span>{options.target_scene_count || 0} 场</span>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <OptionField label="剧本类型" id="option-genre">
          <Input
            id="option-genre"
            placeholder="例如 悬疑、爱情、奇幻"
            value={options.genre || ''}
            onChange={(e) => update('genre', e.target.value)}
          />
          <SuggestionChips
            suggestions={GENRE_SUGGESTIONS}
            selected={options.genre}
            onSelect={(val) => update('genre', val === options.genre ? '' : val)}
          />
        </OptionField>

        <OptionField label="改编风格" id="option-style">
          <Input
            id="option-style"
            placeholder="例如 短剧、影视剧、广播剧"
            value={options.style || ''}
            onChange={(e) => update('style', e.target.value)}
          />
          <SuggestionChips
            suggestions={STYLE_SUGGESTIONS}
            selected={options.style}
            onSelect={(val) => update('style', val === options.style ? '' : val)}
          />
        </OptionField>

        <OptionField label="目标场景数量" id="option-scene-count">
          <Input
            id="option-scene-count"
            type="number"
            min={1}
            max={50}
            placeholder="6"
            value={options.target_scene_count || ''}
            onChange={(e) =>
              update('target_scene_count', e.target.value ? Number(e.target.value) : null)
            }
          />
          <span className="text-xs text-muted-foreground">范围 1～50，建议 6～12</span>
        </OptionField>

        <OptionField label="语言" id="option-language">
          <Input
            id="option-language"
            placeholder="zh-CN"
            value={options.language || ''}
            onChange={(e) => update('language', e.target.value)}
          />
        </OptionField>
      </div>
    </div>
  );
}

export default GenerationOptions;
