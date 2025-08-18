'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export function Header() {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <motion.header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'glass backdrop-blur-md bg-surface/85' : 'bg-transparent'
      }`}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link 
            href="/" 
            className="font-space font-semibold text-xl text-text hover:text-accent transition-colors focus-ring rounded-md px-2 py-1"
          >
            reddit this.
          </Link>
          
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              href="#how-it-works" 
              className="text-muted hover:text-text transition-colors focus-ring rounded-md px-2 py-1"
            >
              How it works
            </Link>
            <Link 
              href="#examples" 
              className="text-muted hover:text-text transition-colors focus-ring rounded-md px-2 py-1"
            >
              Examples
            </Link>
            <Link 
              href="https://github.com" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted hover:text-text transition-colors focus-ring rounded-md px-2 py-1"
            >
              GitHub
            </Link>
            <Link 
              href="/search" 
              className="btn-primary"
            >
              Open app
            </Link>
          </nav>

          {/* Mobile menu button */}
          <button 
            className="md:hidden text-muted hover:text-text transition-colors focus-ring rounded-md p-2"
            aria-label="Open menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </motion.header>
  )
}
