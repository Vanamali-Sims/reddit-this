"use client";

import { useState } from "react";
import { useDraft } from "@/lib/hooks/useDraft";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Copy, ExternalLink, Loader2, AlertCircle } from "lucide-react";
import { Textarea } from "./ui/textarea";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

interface DraftDialogProps {
  isOpen: boolean;
  onClose: () => void;
  originalQuery: string;
}

export function DraftDialog({ isOpen, onClose, originalQuery }: DraftDialogProps) {
  const [region, setRegion] = useState("");
  const { data: draft, isLoading, error, mutate: generateDraft } = useDraft();

  const handleGenerate = () => {
    generateDraft({
      text: originalQuery,
      region: region || undefined,
    });
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // TODO: Add toast notification
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const copyTitle = () => copyToClipboard(draft?.title || "");
  const copyBody = () => copyToClipboard(draft?.body || "");
  const copyBoth = () => copyToClipboard(`${draft?.title}\n\n${draft?.body}`);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Generate Reddit Post Draft</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Configuration */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="region">Region/Country (optional)</Label>
              <Input
                id="region"
                placeholder="e.g., Australia, United States, United Kingdom"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
              <p className="text-xs text-gray-600 mt-1">
                Helps tailor product recommendations and local availability
              </p>
            </div>

            <Button onClick={handleGenerate} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Generating...
                </>
              ) : (
                "Generate Draft"
              )}
            </Button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-red-800">
                <AlertCircle className="h-4 w-4" />
                <span className="font-medium">Generation failed</span>
              </div>
              <p className="text-red-600 mt-1">
                {error instanceof Error ? error.message : "Something went wrong"}
              </p>
            </div>
          )}

          {/* Draft Results */}
          {draft && (
            <div className="space-y-6">
              {/* Generation Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-800 text-sm">
                  Draft generated using {draft.generated_by === "llm" ? "AI" : "template"}
                  {draft.generated_by === "template" && (
                    <span className="ml-1">
                      (Add OpenRouter API key for AI-powered generation)
                    </span>
                  )}
                </p>
              </div>

              {/* Title */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Title ({draft.title.length}/300 characters)</Label>
                  <Button size="sm" variant="ghost" onClick={copyTitle}>
                    <Copy className="h-3 w-3 mr-1" />
                    Copy
                  </Button>
                </div>
                <Input
                  value={draft.title}
                  readOnly
                  className="font-medium"
                />
              </div>

              {/* Body */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Post Body ({draft.body.length}/40000 characters)</Label>
                  <Button size="sm" variant="ghost" onClick={copyBody}>
                    <Copy className="h-3 w-3 mr-1" />
                    Copy
                  </Button>
                </div>
                <Textarea
                  value={draft.body}
                  readOnly
                  className="min-h-[300px] font-mono text-sm"
                />
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t">
                <Button onClick={copyBoth} variant="outline">
                  <Copy className="h-4 w-4 mr-2" />
                  Copy Title + Body
                </Button>

                <div className="flex gap-2">
                  {draft.reddit_submit_url && (
                    <Button asChild>
                      <a
                        href={draft.reddit_submit_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Post to Reddit
                      </a>
                    </Button>
                  )}
                </div>
              </div>

              {/* Tips */}
              <div className="bg-gray-50 rounded-lg p-4 text-sm">
                <h4 className="font-medium text-gray-900 mb-2">Tips for posting:</h4>
                <ul className="text-gray-600 space-y-1">
                  <li>• Review community rules before posting</li>
                  <li>• Consider posting in the most relevant subreddit</li>
                  <li>• Add photos if they help illustrate your concern</li>
                  <li>• Be open to advice and follow-up questions</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
