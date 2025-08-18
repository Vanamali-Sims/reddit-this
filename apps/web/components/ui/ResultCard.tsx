'use client'

import { motion } from 'framer-motion'
import { ExternalLink, Bookmark } from 'lucide-react'

interface ResultCardProps {
  title: string
  snippet: string
  subreddit: string
  score: number
  age: string
  url: string
  onSave?: () => void
}

export function ResultCard({ 
  title, 
  snippet, 
  subreddit, 
  score, 
  age, 
  url, 
  onSave 
}: ResultCardProps) {
  return (
    <motion.article
      className="card group"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      viewport={{ once: true }}
      whileHover={{ y: -4 }}
    >
      <div className="space-y-4">
        <h3 className="font-space font-semibold text-xl leading-tight line-clamp-2 group-hover:text-accent transition-colors duration-200">
          {title}
        </h3>
        
        <p className="text-muted leading-relaxed line-clamp-3">
          {snippet}
        </p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 text-sm text-muted">
            <span className="font-medium text-accent">r/{subreddit}</span>
            <span>•</span>
            <span>{score} points</span>
            <span>•</span>
            <span>{age}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3 pt-2">
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary flex items-center gap-2 text-sm flex-1 justify-center"
          >
            <ExternalLink size={14} />
            Open on Reddit
          </a>
          
          <button
            onClick={onSave}
            className="btn-secondary flex items-center gap-2 text-sm px-4"
            aria-label="Save post"
          >
            <Bookmark size={14} />
            Save
          </button>
        </div>
      </div>
    </motion.article>
  )
}
