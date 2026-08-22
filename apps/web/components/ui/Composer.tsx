'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Edit3, Loader2 } from 'lucide-react'

const exampleQueries = [
  "itchy scalp",
  "student visa work rights", 
  "ray-ban meta pairing",
  "anxiety before job interview",
  "best coffee grinder under $100",
  "meditation for beginners"
]

interface ComposerProps {
  onSearch?: (query: string) => void
  onGenerateDraft?: (query: string) => void
  isLoading?: boolean
}

export function Composer({ onSearch, onGenerateDraft, isLoading = false }: ComposerProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch?.(query.trim())
    }
  }

  const handleExampleClick = (example: string) => {
    setQuery(example)
  }

  const handleGenerateDraft = () => {
    if (query.trim()) {
      onGenerateDraft?.(query.trim())
    }
  }

  // Calculate disabled states
  const hasQuery = query.trim().length > 0
  const isGenerateDisabled = !hasQuery || isLoading
  const isSearchDisabled = !hasQuery || isLoading

  return (
    <motion.section 
      id="composer"
      className="section-padding bg-bg border-t border-line"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      viewport={{ once: true }}
    >
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="relative">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Describe what's on your mind... Like: 'My scalp has been really itchy lately, especially after washing my hair. I've tried different shampoos but nothing seems to help. Has anyone else dealt with this?'"
                className="w-full h-32 p-6 bg-surface rounded-xl border border-line text-text placeholder:text-muted resize-none focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent hover:bg-hover"
                disabled={isLoading}
              />
              
              <div className="absolute bottom-4 right-4 text-sm text-muted">
                {query.length}/1000
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
              <div className="flex flex-wrap gap-2">
                {exampleQueries.map((example, index) => (
                  <motion.button
                    key={example}
                    type="button"
                    onClick={() => handleExampleClick(example)}
                    className="card-minimal text-sm text-muted hover:text-text focus-ring"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    {example}
                  </motion.button>
                ))}
              </div>
              
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleGenerateDraft}
                  disabled={isGenerateDisabled}
                  className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Edit3 size={16} />
                  Generate post
                </button>
                
                <button
                  type="submit"
                  disabled={isSearchDisabled}
                  className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search size={16} />
                      Search
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </motion.section>
  )
}
