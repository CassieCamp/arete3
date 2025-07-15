'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, X, Calendar, Clock, User, Target, TrendingUp, Lightbulb, ChevronLeft, ChevronRight } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { motion, PanInfo, AnimatePresence } from 'framer-motion'
import { UseInsightNavigationResult } from '@/hooks/useInsightNavigation'

interface SessionInsight {
  _id: string
  session_title?: string
  session_date?: string
  session_summary?: string
  key_themes?: string[]
  client_discoveries?: Array<{
    insight: string
    emotional_response: string
  }>
  celebration?: {
    description: string
    significance: string
  }
  action_items?: Array<{
    action: string
    timeline?: string
    accountability_measure?: string
  }>
  intention?: {
    behavior_change: string
    timeline?: string
    support_needed?: string[]
  }
  powerful_questions?: Array<{
    question: string
    impact_description: string
    client_response_summary?: string
  }>
}

interface SessionInsightModalProps {
  insight: any | null  // Using any to match the actual SessionInsightDetail type from the hook
  isOpen: boolean
  onClose: () => void
  loading?: boolean
  error?: string | null
  navigation?: UseInsightNavigationResult
}

export function SessionInsightModal({
  insight,
  isOpen,
  onClose,
  loading = false,
  error,
  navigation
}: SessionInsightModalProps) {
  const router = useRouter()

  const handleBackToJourney = () => {
    onClose()
    router.push('/member/journey')
  }

  const handleClose = () => {
    onClose()
  }

  // Swipe gesture handling
  const handlePan = (event: any, info: PanInfo) => {
    const { offset, velocity } = info
    const swipeThreshold = 50
    const velocityThreshold = 0.3

    // Only handle horizontal swipes
    if (Math.abs(offset.x) > Math.abs(offset.y)) {
      if (offset.x > swipeThreshold || velocity.x > velocityThreshold) {
        // Swipe right - go to previous insight
        if (navigation?.hasPrevious) {
          navigation.navigateToPrevious()
        }
      } else if (offset.x < -swipeThreshold || velocity.x < -velocityThreshold) {
        // Swipe left - go to next insight
        if (navigation?.hasNext) {
          navigation.navigateToNext()
        }
      }
    }
  }

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isOpen) return

      switch (event.key) {
        case 'ArrowLeft':
          event.preventDefault()
          if (navigation?.hasPrevious) {
            navigation.navigateToPrevious()
          }
          break
        case 'ArrowRight':
          event.preventDefault()
          if (navigation?.hasNext) {
            navigation.navigateToNext()
          }
          break
        case 'Escape':
          event.preventDefault()
          handleClose()
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, navigation, handleClose])

  // Loading state
  if (loading) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl w-full mx-4 max-h-[90vh] bg-background/80 backdrop-blur-sm border-border">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground ml-4">Loading session insight...</p>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  // Error state
  if (error) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl w-full mx-4 max-h-[90vh] bg-background/80 backdrop-blur-sm border-border">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              Error Loading Insight
            </h1>
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={handleClose} variant="outline">
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  // No insight found
  if (!insight) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl w-full mx-4 max-h-[90vh] bg-background/80 backdrop-blur-sm border-border">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              Insight Not Found
            </h1>
            <p className="text-muted-foreground mb-4">
              The session insight you're looking for could not be found.
            </p>
            <Button onClick={handleClose} variant="outline">
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[95vw] w-full mx-2 max-h-[95vh] p-0 bg-background border-border shadow-xl sm:max-w-6xl sm:mx-4">
        {/* New Header Design - Simplified and Compact */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-card/50 backdrop-blur-sm rounded-t-lg sm:p-6">
          <div className="flex-1 min-w-0">
            {/* Title and Date on Same Line */}
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-lg font-semibold text-foreground sm:text-xl">
                Insights
              </h1>
              {insight.session_date && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>{new Date(insight.session_date).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>

          {/* Desktop Close Button */}
          <div className="hidden sm:flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
              aria-label="Close insight modal"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Content Area */}
        <div className="p-4 space-y-6 overflow-y-auto max-h-[calc(95vh-140px)] pb-20 sm:p-6 sm:space-y-8 sm:pb-6 relative">
          {/* Key Insights & Discoveries */}
          {insight.client_discoveries && insight.client_discoveries.length > 0 && (
            <section className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Lightbulb className="h-4 w-4 text-primary" />
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Self Discovery</h2>
              </div>
              <div className="space-y-6">
                {insight.client_discoveries.map((discovery: { insight: string; emotional_response: string }, index: number) => (
                  <div key={index} className="group">
                    <div className="bg-background border border-border rounded-lg p-6 hover:shadow-md transition-shadow">
                      <blockquote className="text-xl font-medium text-foreground leading-relaxed mb-4">
                        "{discovery.insight}"
                      </blockquote>
                      <p className="text-base text-muted-foreground">
                        <span className="font-medium">How this felt:</span> {discovery.emotional_response}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Celebration */}
          {insight.celebration && (
            <section className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-secondary/10 flex items-center justify-center">
                  <span className="text-lg">🎉</span>
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Celebration</h2>
              </div>
              <div className="bg-background border border-border rounded-lg p-6 hover:shadow-md transition-shadow">
                <blockquote className="text-xl font-medium text-foreground leading-relaxed mb-4">
                  "{insight.celebration.description}"
                </blockquote>
                <p className="text-base text-muted-foreground">{insight.celebration.significance}</p>
              </div>
            </section>
          )}

          {/* Action Commitments */}
          {insight.action_items && insight.action_items.length > 0 && (
            <section className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center">
                  <Target className="h-4 w-4 text-accent-foreground" />
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Action Commitments</h2>
              </div>
              <div className="space-y-6">
                {insight.action_items.map((item: { action: string; timeline?: string; accountability_measure?: string; }, index: number) => (
                  <div key={index} className="bg-background border border-border rounded-lg p-6 hover:shadow-md transition-shadow">
                    <blockquote className="text-xl font-medium text-foreground leading-relaxed mb-6">
                      "{item.action}"
                    </blockquote>
                    <div className="flex flex-col sm:flex-row sm:flex-wrap gap-3 sm:gap-6 text-sm text-muted-foreground">
                      {item.timeline && (
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0"></span>
                          <span><strong>By when:</strong> {item.timeline}</span>
                        </div>
                      )}
                      {item.accountability_measure && (
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0"></span>
                          <span><strong>How you'll track progress:</strong> {item.accountability_measure}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Future Intentions */}
          {insight.intention && (
            <section className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-chart-1/10 flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-chart-1" />
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Future Intentions</h2>
              </div>
              <div className="bg-background border border-border rounded-lg p-6 hover:shadow-md transition-shadow">
                <blockquote className="text-xl font-medium text-foreground leading-relaxed mb-6">
                  "{insight.intention.behavior_change}"
                </blockquote>
                <div className="space-y-4">
                  {insight.intention.timeline && (
                    <div className="flex items-center gap-2 text-base text-muted-foreground">
                      <span className="w-2 h-2 rounded-full bg-chart-1 flex-shrink-0"></span>
                      <span><strong>Timeline:</strong> {insight.intention.timeline}</span>
                    </div>
                  )}
                  {insight.intention.support_needed && insight.intention.support_needed.length > 0 && (
                    <div>
                      <p className="font-medium text-foreground mb-3 text-base">Support that would help:</p>
                      <ul className="space-y-2">
                        {insight.intention.support_needed.map((support: string, index: number) => (
                          <li key={index} className="flex items-start gap-2 text-base text-muted-foreground">
                            <span className="w-2 h-2 rounded-full bg-chart-1 mt-2 flex-shrink-0"></span>
                            <span>{support}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}

          {/* Powerful Questions */}
          {insight.powerful_questions && insight.powerful_questions.length > 0 && (
            <section className="space-y-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-chart-2/10 flex items-center justify-center">
                  <span className="text-lg">🤔</span>
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Powerful Questions</h2>
              </div>
              <div className="space-y-8">
                {insight.powerful_questions.map((question: { question: string; impact_description: string; client_response_summary?: string; }, index: number) => (
                  <div key={index} className="bg-background border border-border rounded-lg p-6 hover:shadow-md transition-shadow">
                    <blockquote className="text-xl font-medium text-foreground italic leading-relaxed mb-4">
                      "{question.question}"
                    </blockquote>
                    <p className="text-base text-muted-foreground mb-4">{question.impact_description}</p>
                    {question.client_response_summary && (
                      <div className="bg-muted/30 rounded-lg p-4 border-l-4 border-chart-2">
                        <p className="text-base text-foreground">
                          <span className="font-medium">Your reflection:</span> {question.client_response_summary}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Session Overview */}
          <section className="space-y-6 border-t border-border pt-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-muted/50 flex items-center justify-center">
                <span className="text-lg">📝</span>
              </div>
              <h2 className="text-lg font-medium text-muted-foreground">Session Overview</h2>
            </div>
            <div className="bg-muted/20 rounded-lg p-6">
              <p className="text-lg text-foreground leading-relaxed mb-6">
                {insight.session_summary || 'No summary available'}
              </p>
              {insight.key_themes && insight.key_themes.length > 0 && (
                <div>
                  <p className="font-medium text-foreground mb-4 text-base">Key themes we explored:</p>
                  <div className="flex flex-wrap gap-3">
                    {insight.key_themes.map((theme: string, index: number) => (
                      <Badge key={index} variant="secondary" className="px-4 py-2 text-sm">
                        {theme}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Floating Close Button - Bottom Right for Thumb Access (Mobile Only) */}
        <div className="fixed bottom-6 right-6 z-10 sm:hidden">
          <Button
            variant="default"
            size="lg"
            onClick={handleClose}
            className="rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all bg-primary text-primary-foreground"
            aria-label="Close insight modal"
          >
            <X className="h-6 w-6" />
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
// Trigger Vercel redeploy