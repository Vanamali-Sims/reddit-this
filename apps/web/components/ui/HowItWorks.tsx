'use client'

import { motion } from 'framer-motion'
import { Brain, Target, Sparkles } from 'lucide-react'

const steps = [
  {
    icon: Brain,
    title: 'Understands your worry',
    description: 'Our AI analyzes the context and emotion behind your text, not just keywords.'
  },
  {
    icon: Target,
    title: 'Finds relevant subreddits',
    description: 'We discover communities where your specific concern gets the best discussions.'
  },
  {
    icon: Sparkles,
    title: 'Reranks the best posts',
    description: 'Smart scoring surfaces the most helpful threads with real solutions.'
  }
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="section-padding relative">
      <div className="container mx-auto px-6">
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="mb-6">How it works</h2>
          <p className="text-muted max-w-2xl mx-auto">
            Three steps to find your community and get real help from people who understand.
          </p>
        </motion.div>
        
        <div className="grid md:grid-cols-3 gap-12 max-w-5xl mx-auto">
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              className="text-center group"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
            >
              <div className="relative mb-8">
                <div className="w-16 h-16 mx-auto bg-surface border border-line rounded-xl flex items-center justify-center group-hover:bg-hover">
                  <step.icon size={28} strokeWidth={1.5} />
                </div>
                
                {/* Connection line */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-8 left-1/2 w-full h-px bg-line" />
                )}
              </div>
              
              <h3 className="mb-4 text-xl">{step.title}</h3>
              <p className="text-muted leading-relaxed">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
