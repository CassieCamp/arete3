"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { Settings } from "lucide-react";

interface SessionSettingsProps {
  autoSendEnabled?: boolean;
  onAutoSendChange?: (enabled: boolean) => void;
}

export function SessionSettings({ 
  autoSendEnabled = false, 
  onAutoSendChange 
}: SessionSettingsProps) {
  const [isEnabled, setIsEnabled] = useState(autoSendEnabled);

  const handleToggleChange = (checked: boolean) => {
    setIsEnabled(checked);
    onAutoSendChange?.(checked);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Settings className="w-5 h-5 text-primary" />
          </div>
          <div>
            <CardTitle className="text-lg font-serif text-foreground">
              Session Preparation
            </CardTitle>
            <CardDescription>
              Configure how your coaching sessions are prepared
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label 
                htmlFor="auto-send-toggle" 
                className="text-sm font-medium text-foreground"
              >
                Auto-send context summary to coach
              </Label>
              <p className="text-xs text-muted-foreground">
                Automatically share your recent entries and insights with your coach before sessions
              </p>
            </div>
            
            <div className="flex items-center">
              <button
                id="auto-send-toggle"
                role="switch"
                aria-checked={isEnabled}
                onClick={() => handleToggleChange(!isEnabled)}
                className={`
                  relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2
                  ${isEnabled 
                    ? 'bg-primary' 
                    : 'bg-input'
                  }
                `}
              >
                <span
                  className={`
                    inline-block h-4 w-4 transform rounded-full bg-background transition-transform
                    ${isEnabled ? 'translate-x-6' : 'translate-x-1'}
                  `}
                />
              </button>
            </div>
          </div>

          {isEnabled && (
            <div className="mt-4 p-3 bg-muted/50 rounded-lg border">
              <p className="text-xs text-muted-foreground">
                <strong>What gets shared:</strong> Your recent journal entries, goal progress, 
                and key insights from the past week will be automatically compiled and sent 
                to your coach 24 hours before your scheduled session.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}