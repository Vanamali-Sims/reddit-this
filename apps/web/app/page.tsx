'use client'

import { useState } from 'react'
import { Header } from '@/components/ui/Header'
import { Hero } from '@/components/ui/Hero'
import { Composer } from '@/components/ui/Composer'
import { HowItWorks } from '@/components/ui/HowItWorks'
import { ResultCard } from '@/components/ui/ResultCard'
import { CTA } from '@/components/ui/CTA'
import { Footer } from '@/components/ui/Footer'
import { motion } from 'framer-motion'
import { formatDistanceToNow } from 'date-fns'

type ResultView = {
  id: string
  title: string
  snippet: string
  subreddit: string
  score: number
  age: string
  url: string
}

type ApiPost = {
  id: string
  title: string
  selftext?: string
  subreddit: string
  score?: number
  created_utc?: string
  url?: string
  permalink?: string
}

function formatAge(createdUtc?: string) {
  if (!createdUtc) return ''
  const parsed = new Date(createdUtc)
  if (Number.isNaN(parsed.getTime())) return ''
  return formatDistanceToNow(parsed, { addSuffix: true })
}

function mapPost(post: ApiPost): ResultView {
  const permalink = post.permalink
    ? post.permalink.startsWith('http')
      ? post.permalink
      : `https://reddit.com${post.permalink}`
    : undefined

  return {
    id: post.id,
    title: post.title,
    snippet: post.selftext?.trim() || 'No text in this post.',
    subreddit: post.subreddit,
    score: post.score ?? 0,
    age: formatAge(post.created_utc),
    url: post.url || permalink || '#',
  }
}

export default function HomePage() {
  const [searchResults, setSearchResults] = useState<ResultView[] | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    setSearchError(null)

    try {
      const response = await fetch('/api/ingest/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query, max_results: 12 }),
      })

      if (!response.ok) {
        const body = await response.json().catch(() => null)
        const detail = body?.detail
        const message =
          typeof detail === 'string' ? detail : `Search failed (${response.status})`
        throw new Error(message)
      }

      const data = await response.json()
      setSearchResults((data.posts || []).map(mapPost))
    } catch (error) {
      setSearchResults(null)
      setSearchError(
        error instanceof Error && error.message
          ? error.message
          : 'Could not reach the API. Start it with pnpm dev:api.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateDraft = async (query: string) => {
    console.log('Generate draft for:', query)
  }

  const handleSaveResult = (id: string) => {
    console.log('Save result:', id)
  }

  return (
    <div className="min-h-screen bg-bg text-text">
      <Header />
      
      <main>
        <Hero />
        
        <Composer 
          onSearch={handleSearch}
          onGenerateDraft={handleGenerateDraft}
          isLoading={isLoading}
        />

        {searchError && (
          <section className="section-padding pt-0">
            <div className="container mx-auto px-6">
              <div className="max-w-4xl mx-auto card text-muted">
                {searchError}
              </div>
            </div>
          </section>
        )}
        
        {searchResults && (
          <motion.section 
            className="section-padding"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <div className="container mx-auto px-6">
              <div className="mb-12">
                <h2 className="mb-4">
                  {searchResults.length > 0
                    ? `Found ${searchResults.length} relevant discussions`
                    : 'No matching discussions yet'}
                </h2>
                <p className="text-muted">
                  Ranked by relevance, helpfulness, and community engagement.
                </p>
              </div>
              
              <div className="grid lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
                {searchResults.map((result, index) => (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                  >
                    <ResultCard
                      title={result.title}
                      snippet={result.snippet}
                      subreddit={result.subreddit}
                      score={result.score}
                      age={result.age}
                      url={result.url}
                      onSave={() => handleSaveResult(result.id)}
                    />
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.section>
        )}
        
        <HowItWorks />
        <CTA />
      </main>
      
      <Footer />
    </div>
  )
}
