"use client";

import { formatDistanceToNow } from "date-fns";
import { ExternalLink, MessageCircle, TrendingUp, Clock, Target } from "lucide-react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

interface PostCardProps {
  post: {
    id: string;
    title: string;
    selftext?: string;
    author: string;
    score: number;
    num_comments: number;
    url: string;
    permalink: string;
    created_utc: string;
    subreddit: string;
    ranking_scores?: {
      composite: number;
      semantic_similarity: number;
      recency_score: number;
      subreddit_quality: number;
      score_normalized: number;
      comments_normalized: number;
    };
  };
}

export function PostCard({ post }: PostCardProps) {
  const createdDate = new Date(post.created_utc);
  const timeAgo = formatDistanceToNow(createdDate, { addSuffix: true });
  
  const redditUrl = `https://reddit.com${post.permalink}`;
  const subredditUrl = `https://reddit.com/r/${post.subreddit}`;

  // Truncate selftext for display
  const truncatedText = post.selftext && post.selftext.length > 300
    ? post.selftext.substring(0, 300) + "..."
    : post.selftext;

  const relevanceScore = post.ranking_scores?.composite;
  const semanticSimilarity = post.ranking_scores?.semantic_similarity;

  return (
    <div className="bg-white rounded-lg border hover:shadow-md transition-shadow p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <a
            href={subredditUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-blue-600 hover:underline"
          >
            r/{post.subreddit}
          </a>
          <span>•</span>
          <span>u/{post.author}</span>
          <span>•</span>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {timeAgo}
          </div>
        </div>
        
        {relevanceScore && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Target className="h-3 w-3" />
            {(relevanceScore * 100).toFixed(0)}% match
          </div>
        )}
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-3 leading-tight">
        {post.title}
      </h3>

      {/* Content preview */}
      {truncatedText && (
        <p className="text-gray-700 mb-4 leading-relaxed">
          {truncatedText}
        </p>
      )}

      {/* Metadata */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <TrendingUp className="h-4 w-4" />
            {post.score} points
          </div>
          <div className="flex items-center gap-1">
            <MessageCircle className="h-4 w-4" />
            {post.num_comments} comments
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Ranking breakdown */}
          {post.ranking_scores && (
            <div className="flex gap-1">
              {semanticSimilarity && semanticSimilarity > 0.7 && (
                <Badge variant="secondary" className="text-xs">
                  High relevance
                </Badge>
              )}
              {post.ranking_scores.recency_score > 0.8 && (
                <Badge variant="secondary" className="text-xs">
                  Recent
                </Badge>
              )}
            </div>
          )}
          
          <Button size="sm" variant="outline" asChild>
            <a
              href={redditUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1"
            >
              <ExternalLink className="h-3 w-3" />
              View on Reddit
            </a>
          </Button>
        </div>
      </div>

      {/* Debug info (only in development) */}
      {process.env.NODE_ENV === "development" && post.ranking_scores && (
        <details className="mt-4 text-xs text-gray-500">
          <summary className="cursor-pointer">Ranking Details</summary>
          <div className="mt-2 space-y-1">
            <div>Composite: {(post.ranking_scores.composite * 100).toFixed(1)}%</div>
            <div>Semantic: {(post.ranking_scores.semantic_similarity * 100).toFixed(1)}%</div>
            <div>Recency: {(post.ranking_scores.recency_score * 100).toFixed(1)}%</div>
            <div>Quality: {(post.ranking_scores.subreddit_quality * 100).toFixed(1)}%</div>
          </div>
        </details>
      )}
    </div>
  );
}
