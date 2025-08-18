"use client";

import { useState } from "react";
import { Search, Loader2, Sparkles } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

interface SearchBoxProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export function SearchBox({ onSearch, isLoading }: SearchBoxProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleSubmit(e);
    }
  };

  return (
    <div className="glass-card rounded-3xl p-8 lg:p-10">
      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="relative">
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What's on your mind? Share anything you'd like to explore or get advice about..."
            className="min-h-[160px] resize-none text-lg font-light bg-transparent border-0 p-0 focus:ring-0 placeholder:text-gray-400 text-gray-800 leading-relaxed"
            disabled={isLoading}
          />
          <div className="absolute bottom-2 right-2 text-xs text-gray-400 font-light">
            ⌘ + Enter
          </div>
        </div>
        
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-500 font-light">
            {query.length}/1000
          </div>
          
          <Button
            type="submit"
            disabled={!query.trim() || isLoading || query.length > 1000}
            className="bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white font-light text-lg px-10 py-4 rounded-2xl button-glow transition-all duration-500 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none border-0"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin mr-3" />
                Discovering
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5 mr-3" />
                Reddit this
              </>
            )}
          </Button>
        </div>
        
        {query.length > 1000 && (
          <div className="glass-card rounded-2xl p-6 border-l-4 border-red-500/60">
            <p className="text-sm text-red-600 font-light">
              A bit too long — please keep it under 1000 characters for the best results.
            </p>
          </div>
        )}
      </form>
    </div>
  );
}
