"use client";

import { useState } from "react";
import { PostCard } from "./PostCard";
import { SubredditChips } from "./SubredditChips";
import { DraftDialog } from "./DraftDialog";
import { Button } from "./ui/button";
import { PenTool, Filter } from "lucide-react";
import { Badge } from "./ui/badge";

interface SearchResultsProps {
  results: {
    query: any;
    subreddits: any[];
    posts: any[];
    metadata: any;
  };
  query: string;
  isLoading?: boolean;
}

export function SearchResults({ results, query, isLoading }: SearchResultsProps) {
  const [showDraftDialog, setShowDraftDialog] = useState(false);
  const [selectedSubreddits, setSelectedSubreddits] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<"relevance" | "recency" | "score">("relevance");

  const filteredPosts = results.posts.filter(post => 
    selectedSubreddits.length === 0 || selectedSubreddits.includes(post.subreddit)
  );

  const sortedPosts = [...filteredPosts].sort((a, b) => {
    switch (sortBy) {
      case "recency":
        return new Date(b.created_utc).getTime() - new Date(a.created_utc).getTime();
      case "score":
        return b.score - a.score;
      default: // relevance
        return (b.ranking_scores?.composite || 0) - (a.ranking_scores?.composite || 0);
    }
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        {/* Loading Skeletons */}
        <div className="space-y-4">
          <div className="h-6 bg-gray-200 rounded animate-pulse"></div>
          <div className="flex gap-2">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-8 w-24 bg-gray-200 rounded animate-pulse"></div>
            ))}
          </div>
        </div>
        
        <div className="grid gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white rounded-lg border p-6 space-y-3">
              <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-3 bg-gray-200 rounded animate-pulse w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded animate-pulse w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with metadata */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Search Results
            </h2>
            <p className="text-gray-600">
              Found {results.posts.length} posts across {results.subreddits.length} communities
              in {results.metadata.processing_time_seconds.toFixed(2)}s
            </p>
          </div>
          
          <Button
            onClick={() => setShowDraftDialog(true)}
            className="flex items-center gap-2"
          >
            <PenTool className="h-4 w-4" />
            Write My Post
          </Button>
        </div>

        {/* Query breakdown */}
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Key phrases extracted:</p>
          <div className="flex flex-wrap gap-2">
            {results.query.keyphrases.map((phrase: string, i: number) => (
              <Badge key={i} variant="secondary">
                {phrase}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      {/* Subreddit chips */}
      <SubredditChips
        subreddits={results.subreddits}
        selectedSubreddits={selectedSubreddits}
        onSelectionChange={setSelectedSubreddits}
      />

      {/* Filters and sorting */}
      <div className="flex items-center justify-between bg-white rounded-lg border p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium">Sort by:</span>
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="relevance">Relevance</option>
            <option value="recency">Most Recent</option>
            <option value="score">Highest Score</option>
          </select>
        </div>
        
        <div className="text-sm text-gray-600">
          Showing {sortedPosts.length} of {results.posts.length} posts
        </div>
      </div>

      {/* Posts */}
      <div className="space-y-4">
        {sortedPosts.length > 0 ? (
          sortedPosts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))
        ) : (
          <div className="bg-white rounded-lg border p-8 text-center">
            <p className="text-gray-600">
              No posts found matching the selected filters.
            </p>
          </div>
        )}
      </div>

      {/* Draft Dialog */}
      <DraftDialog
        isOpen={showDraftDialog}
        onClose={() => setShowDraftDialog(false)}
        originalQuery={query}
      />
    </div>
  );
}
