import MarkdownIt from "markdown-it";

const markdown = new MarkdownIt({ html: false, linkify: true });

export function MarkdownContent({ source, className = "" }: { source: string; className?: string }) {
  return <div className={className} dangerouslySetInnerHTML={{ __html: markdown.render(source) }} />;
}
