'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Github, Twitter } from 'lucide-react'

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <motion.footer 
      className="border-t border-line py-16"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
      viewport={{ once: true }}
    >
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8 mb-12">
          <div>
            <h4 className="font-space font-semibold text-lg mb-4 text-text">reddit this<span className="text-accent">.</span></h4>
            <p className="text-muted text-sm leading-relaxed">
              Find meaningful conversations and get advice from Reddit communities that matter.
            </p>
          </div>
          
          <div>
            <h5 className="font-instrument font-medium mb-4 text-text">Product</h5>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="#how-it-works" className="text-muted hover:text-text">
                  How it works
                </Link>
              </li>
              <li>
                <Link href="#examples" className="text-muted hover:text-text">
                  Examples
                </Link>
              </li>
              <li>
                <span className="text-muted opacity-50">API (coming soon)</span>
              </li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-instrument font-medium mb-4 text-text">Company</h5>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="text-muted hover:text-text">
                  About
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-muted hover:text-text">
                  Privacy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-muted hover:text-text">
                  Terms
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-instrument font-medium mb-4 text-text">Connect</h5>
            <div className="flex gap-3">
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="w-8 h-8 bg-surface border border-line rounded-lg flex items-center justify-center text-muted hover:text-text hover:bg-hover"
                aria-label="GitHub"
              >
                <Github size={16} />
              </a>
              <a 
                href="https://twitter.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="w-8 h-8 bg-surface border border-line rounded-lg flex items-center justify-center text-muted hover:text-text hover:bg-hover"
                aria-label="Twitter"
              >
                <Twitter size={16} />
              </a>
            </div>
          </div>
        </div>
        
        <div className="pt-8 border-t border-line flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-muted text-sm">
            © {currentYear} reddit this. All rights reserved.
          </p>
          
          <p className="text-muted text-xs opacity-70">
            Made in Melbourne by Sims from Vizag ✨
          </p>
        </div>
      </div>
    </motion.footer>
  )
}
