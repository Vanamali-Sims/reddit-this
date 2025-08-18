'use client'

import { motion } from 'framer-motion'
import { Bell } from 'lucide-react'
import { useState } from 'react'

export function CTA() {
  const [showDialog, setShowDialog] = useState(false)

  return (
    <>
      <motion.section 
        className="section-padding border-t border-accent/20 bg-gradient-to-r from-surface to-surface/50"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
      >
        <div className="container mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="mb-6">Never miss the conversation</h2>
            <p className="text-muted text-xl mb-8 max-w-2xl mx-auto">
              Get notified when new discussions match your interests.
            </p>
            
            <button 
              onClick={() => setShowDialog(true)}
              className="btn-primary text-lg px-8 py-4 flex items-center gap-3 mx-auto"
            >
              <Bell size={20} />
              Set an alert (coming soon)
            </button>
          </motion.div>
        </div>
      </motion.section>

      {/* Coming Soon Dialog */}
      {showDialog && (
        <motion.div
          className="fixed inset-0 bg-bg/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setShowDialog(false)}
        >
          <motion.div
            className="card max-w-md w-full text-center"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-6">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Bell className="text-accent" size={24} />
              </div>
              <h3 className="text-xl font-space font-semibold mb-2">Alerts coming soon</h3>
              <p className="text-muted">
                We're working on smart alerts that notify you when relevant discussions start. 
                Stay tuned!
              </p>
            </div>
            
            <button 
              onClick={() => setShowDialog(false)}
              className="btn-primary w-full"
            >
              Got it
            </button>
          </motion.div>
        </motion.div>
      )}
    </>
  )
}
