'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

interface DoodleProps {
  variant?: 'hero' | 'section'
}

const doodleElements = [
  // Squiggle
  <svg width="40" height="30" viewBox="0 0 40 30" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 15C8 8, 16 22, 24 10C32 -2, 38 15, 38 15" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round"/>
  </svg>,
  
  // Star
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L14.09 8.26L20 10L14.09 11.74L12 18L9.91 11.74L4 10L9.91 8.26L12 2Z" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinejoin="round"/>
  </svg>,
  
  // Arc
  <svg width="36" height="20" viewBox="0 0 36 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 18C8 6, 14 2, 20 2C26 2, 32 6, 34 18" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round"/>
  </svg>,
  
  // Circle
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="14" cy="14" r="12" stroke="currentColor" strokeWidth="1.5" fill="none"/>
  </svg>,
  
  // Cross
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 2V18M2 10H18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>,
  
  // Zigzag
  <svg width="32" height="16" viewBox="0 0 32 16" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 14L8 2L16 14L24 2L30 14" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>,
  
  // Double arc
  <svg width="40" height="24" viewBox="0 0 40 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 20C10 8, 18 8, 26 20" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round"/>
    <path d="M6 16C12 8, 18 8, 24 16" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round"/>
  </svg>,
  
  // Triangle
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 4L20 18H4L12 4Z" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinejoin="round"/>
  </svg>
]

const heroPositions = [
  { top: '15%', left: '10%', delay: 0 },
  { top: '25%', right: '15%', delay: 1.2 },
  { top: '45%', left: '8%', delay: 2.4 },
  { top: '60%', right: '20%', delay: 0.8 },
  { top: '35%', left: '85%', delay: 1.8 },
  { top: '70%', left: '75%', delay: 3.0 },
  { top: '20%', left: '50%', delay: 2.0 },
  { top: '80%', left: '25%', delay: 1.5 }
]

export function Doodles({ variant = 'hero' }: DoodleProps) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)
    
    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }
    
    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  if (variant === 'hero') {
    return (
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {heroPositions.map((position, index) => (
          <motion.div
            key={index}
            className="absolute text-accent opacity-20"
            style={{
              top: position.top,
              left: position.left,
              right: position.right,
              mixBlendMode: 'screen'
            }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ 
              opacity: 0.2, 
              scale: 1,
              y: prefersReducedMotion ? 0 : [-3, 3, -3],
            }}
            transition={{ 
              duration: 0.8,
              delay: position.delay,
              y: {
                duration: 6 + (index * 0.5),
                repeat: prefersReducedMotion ? 0 : Infinity,
                repeatType: 'reverse',
                ease: 'easeInOut'
              }
            }}
          >
            {doodleElements[index % doodleElements.length]}
          </motion.div>
        ))}
      </div>
    )
  }

  return null
}
