'use client'

import { motion } from 'framer-motion'
import { Doodles } from './Doodles'

export function Hero() {
  const scrollToComposer = () => {
    const composer = document.getElementById('composer')
    if (composer) {
      composer.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const scrollToExamples = () => {
    const examples = document.getElementById('examples')
    if (examples) {
      examples.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <section className="relative min-h-screen flex items-center justify-center vignette overflow-hidden">
      <Doodles variant="hero" />
      
      <div className="container mx-auto px-6 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h1 className="mb-8 max-w-4xl mx-auto">
            Find your corner of{' '}
            <span className="accent-gradient">Reddit</span>.
          </h1>
          
          <motion.p 
            className="body-large text-muted max-w-2xl mx-auto mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Type a worry. We surface the best threads—smart, not keyword-dumb.
          </motion.p>
          
          <motion.div 
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <button 
              onClick={scrollToComposer}
              className="btn-primary text-lg px-8 py-4"
            >
              Try it now
            </button>
            <button 
              onClick={scrollToExamples}
              className="btn-secondary text-lg px-8 py-4"
            >
              See examples
            </button>
          </motion.div>
        </motion.div>
      </div>
      
      {/* Subtle glow behind headline */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-96 h-96 bg-accent-amber rounded-full opacity-[0.08] blur-3xl" />
      </div>
    </section>
  )
}
