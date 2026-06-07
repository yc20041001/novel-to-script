const CHAPTER_PATTERNS = [
  /^(第[一二三四五六七八九十百千零〇两\d０-９]+章(?:\s+|[：:、.\-—])?.*)$/i,
  /^(章节[一二三四五六七八九十百千零〇两\d０-９]+(?:\s+|[：:、.\-—])?.*)$/i,
  /^(Chapter\s+[A-Za-z0-9０-９]+(?:\s+|[：:、.\-—])?.*)$/i,
];

/**
 * 将小说全文解析为章节列表。
 *
 * @param {string} text - 文件全文
 * @returns {{ title: string, content: string }[]}
 */
export function parseNovelFile(text) {
  const normalizedText = normalizeText(text);

  if (!normalizedText) {
    return [];
  }

  const lines = normalizedText.split('\n');

  const chapterBoundaries = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    for (const pattern of CHAPTER_PATTERNS) {
      const match = line.match(pattern);
      if (match) {
        chapterBoundaries.push({ lineIndex: i, title: match[1].trim() });
        break;
      }
    }
  }

  if (chapterBoundaries.length >= 2) {
    return splitByChapters(lines, chapterBoundaries);
  }

  if (chapterBoundaries.length === 1) {
    const idx = chapterBoundaries[0].lineIndex;
    const before = lines.slice(0, idx).join('\n').trim();
    const after = lines.slice(idx + 1).join('\n').trim();
    const parts = [];
    if (before) {
      parts.push({ title: '引子', content: before });
    }

    const remainingCount = Math.max(3 - parts.length, 1);
    const remaining = splitEvenly(after, remainingCount, chapterBoundaries[0].title);
    parts.push(...remaining);
    return ensureMinimumChapters(parts);
  }

  return splitEvenly(normalizedText, 3);
}

function splitByChapters(lines, boundaries) {
  const chapters = [];

  for (let i = 0; i < boundaries.length; i++) {
    const start = boundaries[i].lineIndex;
    const end = i + 1 < boundaries.length ? boundaries[i + 1].lineIndex : lines.length;

    const contentLines = lines.slice(start + 1, end);
    const content = contentLines.join('\n').trim();

    chapters.push({
      title: boundaries[i].title,
      content,
    });
  }

  return ensureMinimumChapters(chapters);
}

function splitEvenly(text, count, firstTitle = '') {
  const cleanText = text.trim();
  if (!cleanText) {
    return [];
  }

  const totalLen = cleanText.length;
  const segLen = Math.max(1, Math.ceil(totalLen / count));
  const parts = [];

  for (let i = 0; i < count; i++) {
    const start = i * segLen;
    const end = Math.min(start + segLen, totalLen);
    const segment = cleanText.slice(start, end).trim();
    if (segment) {
      parts.push({
        title: i === 0 && firstTitle ? firstTitle : `第${i + 1}章`,
        content: segment,
      });
    }
  }

  return parts;
}

function ensureMinimumChapters(parts) {
  const filtered = parts.filter((part) => part.title.trim() || part.content.trim());
  if (filtered.length >= 3) {
    return filtered;
  }

  const combined = filtered.map((part) => part.content).join('\n\n').trim();
  if (combined) {
    return splitEvenly(combined, 3);
  }

  return filtered;
}

function normalizeText(text) {
  if (typeof text !== 'string') {
    return '';
  }

  return text
    .replace(/\r\n?/g, '\n')
    .replace(/\u3000/g, ' ')
    .trim();
}
