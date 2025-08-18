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

// Mock data for demonstration
const mockResults = [
  {
    id: '1',
    title: 'Finally found what works for my itchy scalp after years of struggling',
    snippet: 'I used to have the exact same problem! Turns out it was seborrheic dermatitis. What helped me was switching to a sulfate-free shampoo and using tea tree oil twice a week. Also, I found that stress was a huge trigger...',
    subreddit: 'SkincareAddiction',
    score: 847,
    age: '2 days ago',
    url: 'https://reddit.com/r/SkincareAddiction/comments/example'
  },
  {
    id: '2',
    title: 'PSA: Check your pillowcase! It solved my scalp issues completely',
    snippet: 'This might sound weird but changing my pillowcase every 2 days completely eliminated my itchy scalp. I was using fabric softener that was irritating my skin. Cotton pillowcases and fragrance-free detergent made all the difference...',
    subreddit: 'Hair',
    score: 423,
    age: '5 days ago',
    url: 'https://reddit.com/r/Hair/comments/example'
  },
  {
    id: '3',
    title: 'Dermatologist here: Common causes of scalp irritation',
    snippet: 'Board-certified dermatologist here. The most common causes I see are: 1) Over-washing (strips natural oils), 2) Product buildup, 3) Fungal infections, 4) Contact dermatitis from fragrances. Try a clarifying shampoo first...',
    subreddit: 'Dermatology',
    score: 1204,
    age: '1 week ago',
    url: 'https://reddit.com/r/Dermatology/comments/example'
  }
]

export default function HomePage() {
  const [searchResults, setSearchResults] = useState<typeof mockResults | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      setSearchResults(mockResults)
      setIsLoading(false)
    }, 1500)
  }

  const handleGenerateDraft = async (query: string) => {
    // TODO: Implement draft generation
    console.log('Generate draft for:', query)
  }

  const handleSaveResult = (id: string) => {
    // TODO: Implement save functionality
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
        
        {/* Results Section */}
        {searchResults && (
          <motion.section 
            className="section-padding"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <div className="container mx-auto px-6">
              <div className="mb-12">
                <h2 className="mb-4">Found {searchResults.length} relevant discussions</h2>
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