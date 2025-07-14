'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';
import { useCoachingInterestSubmissions } from '@/hooks/useCoachingInterestSubmissions';
import { Mail, Calendar, Target, CheckCircle, Loader2 } from 'lucide-react';
import { format } from 'date-fns';

export function CoachingInterestList() {
  const { submissions, loading, error } = useCoachingInterestSubmissions();

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
      return 'Invalid date';
    }
  };

  const formatDateTime = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy h:mm a');
    } catch {
      return 'Invalid date';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center space-x-2 text-muted-foreground">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading coaching interest submissions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive">
        <div className="flex items-center space-x-2">
          <span className="font-medium">Error loading submissions:</span>
          <span>{error}</span>
        </div>
      </Alert>
    );
  }

  if (submissions.length === 0) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center">
            <Mail className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">No submissions yet</h3>
            <p className="text-muted-foreground">
              Coaching interest submissions will appear here when people fill out the form.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Mail className="w-6 h-6 text-primary" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Total Submissions</p>
                <p className="text-2xl font-semibold text-foreground">{submissions.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-accent/10 rounded-lg">
                <CheckCircle className="w-6 h-6 text-accent" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Email Permissions</p>
                <p className="text-2xl font-semibold text-foreground">
                  {submissions.filter(s => s.email_permission).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Submissions List */}
      <Card>
        <CardHeader>
          <CardTitle>Coaching Interest Submissions</CardTitle>
          <CardDescription>
            All coaching interest form submissions from potential clients.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {submissions.map((submission) => (
              <div
                key={submission.id}
                className="border rounded-lg p-6 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-full">
                      <Mail className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground">{submission.name}</h3>
                      <p className="text-sm text-muted-foreground">{submission.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {submission.email_permission && (
                      <Badge variant="secondary" className="bg-accent/10 text-accent">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Email OK
                      </Badge>
                    )}
                    <div className="text-right">
                      <div className="text-xs text-muted-foreground flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {formatDateTime(submission.created_at)}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center space-x-2 mb-2">
                      <Target className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm font-medium text-foreground">Goals & Interests</span>
                    </div>
                    <div className="bg-muted/30 rounded-md p-3">
                      <p className="text-sm text-foreground whitespace-pre-wrap">
                        {submission.goals}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}