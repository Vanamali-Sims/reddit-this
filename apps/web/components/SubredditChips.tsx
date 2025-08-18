"use client";

import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Check, X } from "lucide-react";

interface SubredditChipsProps {
  subreddits: Array<{
    name: string;
    title: string;
    relevance_score: number;
    quality_score: number;
  }>;
  selectedSubreddits: string[];
  onSelectionChange: (selected: string[]) => void;
}

export function SubredditChips({
  subreddits,
  selectedSubreddits,
  onSelectionChange,
}: SubredditChipsProps) {
  const toggleSubreddit = (subredditName: string) => {
    if (selectedSubreddits.includes(subredditName)) {
      onSelectionChange(selectedSubreddits.filter(name => name !== subredditName));
    } else {
      onSelectionChange([...selectedSubreddits, subredditName]);
    }
  };

  const clearAll = () => onSelectionChange([]);
  const selectAll = () => onSelectionChange(subreddits.map(s => s.name));

  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-gray-900">Relevant Communities</h3>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={selectAll}
            className="text-xs"
          >
            Select All
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={clearAll}
            className="text-xs"
          >
            Clear
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {subreddits.map((subreddit) => {
          const isSelected = selectedSubreddits.includes(subreddit.name);
          const relevancePercentage = Math.round(subreddit.relevance_score * 100);
          
          return (
            <button
              key={subreddit.name}
              onClick={() => toggleSubreddit(subreddit.name)}
              className={`
                inline-flex items-center gap-2 px-3 py-2 rounded-md border transition-colors
                ${isSelected
                  ? 'bg-blue-50 border-blue-200 text-blue-800'
                  : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <span className="font-medium">r/{subreddit.name}</span>
              <span className="text-xs opacity-75">
                {relevancePercentage}%
              </span>
              {isSelected && <Check className="h-3 w-3" />}
            </button>
          );
        })}
      </div>

      {selectedSubreddits.length > 0 && (
        <div className="mt-3 pt-3 border-t text-sm text-gray-600">
          Filtering by {selectedSubreddits.length} of {subreddits.length} communities
        </div>
      )}
    </div>
  );
}
