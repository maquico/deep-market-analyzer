'use client'

import { memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export const MarkdownRenderer = memo(function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div className={cn('markdown-content', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Override link behavior for security
          a: ({ children, href, ...props }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:text-primary/80 underline"
              {...props}
            >
              {children}
            </a>
          ),
          // Customize code blocks
          code: ({ children, className, ...props }) => {
            const isInline = !className?.includes('language-')
            
            if (isInline) {
              return (
                <code 
                  className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono text-foreground"
                  {...props}
                >
                  {children}
                </code>
              )
            }
            
            return (
              <code 
                className="block bg-muted p-3 rounded-md text-xs font-mono text-foreground whitespace-pre-wrap overflow-x-auto"
                {...props}
              >
                {children}
              </code>
            )
          },
          // Make sure tables are responsive
          table: ({ children, ...props }) => (
            <div className="overflow-x-auto mb-2">
              <table className="w-full text-xs border-collapse border border-border" {...props}>
                {children}
              </table>
            </div>
          ),
          // Custom list styling with better spacing
          ul: ({ children, ...props }) => (
            <ul className="text-sm space-y-1 mb-2 pl-6 list-disc text-foreground marker:text-foreground" {...props}>
              {children}
            </ul>
          ),
          ol: ({ children, ...props }) => (
            <ol className="text-sm space-y-1 mb-2 pl-6 list-decimal text-foreground marker:text-foreground" {...props}>
              {children}
            </ol>
          ),
          li: ({ children, ...props }) => (
            <li className="leading-relaxed text-foreground" {...props}>
              {children}
            </li>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
})