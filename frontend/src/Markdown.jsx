function splitTableRow(line) {
  return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((cell) => cell.trim())
}

function isTableDivider(line) {
  return splitTableRow(line).every((cell) => /^:?-{3,}:?$/.test(cell))
}

function isBlockStart(lines, index) {
  const line = lines[index]
  return /^\s*```/.test(line)
    || /^\s{0,3}#{1,6}\s+/.test(line)
    || /^\s*[-*+]\s+/.test(line)
    || /^\s*\d+[.)]\s+/.test(line)
    || (index + 1 < lines.length && line.includes('|') && isTableDivider(lines[index + 1]))
}

function InlineMarkdown({ text }) {
  const tokens = /(`[^`]+`|\*\*.+?\*\*|__.+?__)/g
  return text.split(tokens).map((part, index) => {
    if (part.startsWith('`') && part.endsWith('`')) return <code key={index}>{part.slice(1, -1)}</code>
    if ((part.startsWith('**') && part.endsWith('**')) || (part.startsWith('__') && part.endsWith('__'))) {
      return <strong key={index}>{part.slice(2, -2)}</strong>
    }
    return part
  })
}

export default function Markdown({ content }) {
  const lines = String(content ?? '').split(/\r?\n/)
  const blocks = []
  let index = 0

  while (index < lines.length) {
    const line = lines[index]
    if (!line.trim()) { index += 1; continue }

    const fence = line.match(/^\s*```([\w+-]*)\s*$/)
    if (fence) {
      const codeLines = []
      index += 1
      while (index < lines.length && !/^\s*```\s*$/.test(lines[index])) codeLines.push(lines[index++])
      if (index < lines.length) index += 1
      blocks.push(<pre key={`code-${blocks.length}`}><code className={fence[1] ? `language-${fence[1]}` : undefined}>{codeLines.join('\n')}</code></pre>)
      continue
    }

    const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$/)
    if (heading) {
      const Heading = `h${heading[1].length}`
      blocks.push(<Heading key={`heading-${blocks.length}`}><InlineMarkdown text={heading[2]} /></Heading>)
      index += 1
      continue
    }

    if (index + 1 < lines.length && line.includes('|') && isTableDivider(lines[index + 1])) {
      const headers = splitTableRow(line)
      const alignments = splitTableRow(lines[index + 1]).map((cell) => (
        cell.startsWith(':') && cell.endsWith(':') ? 'center' : cell.endsWith(':') ? 'right' : cell.startsWith(':') ? 'left' : undefined
      ))
      index += 2
      const rows = []
      while (index < lines.length && lines[index].trim() && lines[index].includes('|')) rows.push(splitTableRow(lines[index++]))
      blocks.push(<div className="markdown-table-scroll" key={`table-${blocks.length}`}>
        <table>
          <thead><tr>{headers.map((cell, i) => <th key={i} style={{ textAlign: alignments[i] }}><InlineMarkdown text={cell} /></th>)}</tr></thead>
          <tbody>{rows.map((row, rowIndex) => <tr key={rowIndex}>{headers.map((_, i) => <td key={i} style={{ textAlign: alignments[i] }}><InlineMarkdown text={row[i] || ''} /></td>)}</tr>)}</tbody>
        </table>
      </div>)
      continue
    }

    const bullet = line.match(/^\s*[-*+]\s+(.+)$/)
    const numbered = line.match(/^\s*\d+[.)]\s+(.+)$/)
    if (bullet || numbered) {
      const ordered = Boolean(numbered)
      const List = ordered ? 'ol' : 'ul'
      const items = []
      while (index < lines.length) {
        const item = lines[index].match(ordered ? /^\s*\d+[.)]\s+(.+)$/ : /^\s*[-*+]\s+(.+)$/)
        if (!item) break
        items.push(<li key={items.length}><InlineMarkdown text={item[1]} /></li>)
        index += 1
      }
      blocks.push(<List key={`list-${blocks.length}`}>{items}</List>)
      continue
    }

    const paragraph = [line]
    index += 1
    while (index < lines.length && lines[index].trim() && !isBlockStart(lines, index)) paragraph.push(lines[index++])
    blocks.push(<p key={`paragraph-${blocks.length}`}><InlineMarkdown text={paragraph.join('\n')} /></p>)
  }

  return <div className="markdown-content">{blocks}</div>
}
