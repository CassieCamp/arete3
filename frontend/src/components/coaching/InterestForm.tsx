"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useApiClient } from "@/utils/api";
import { Send, CheckCircle } from "lucide-react";

// Validation schema matching the backend CoachingInterestCreate schema
const interestFormSchema = z.object({
  name: z.string().min(1, "Name is required").trim(),
  email: z.string().email("Please enter a valid email address"),
  goals: z.string().min(1, "Goals are required").trim(),
  email_permission: z.boolean().refine((val) => val === true, {
    message: "Email permission must be granted to proceed"
  })
});

type InterestFormData = z.infer<typeof interestFormSchema>;

interface InterestFormProps {
  onSuccess?: () => void;
}

export function InterestForm({ onSuccess }: InterestFormProps) {
  const { makeApiCall } = useApiClient();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<InterestFormData>({
    resolver: zodResolver(interestFormSchema),
    defaultValues: {
      name: "",
      email: "",
      goals: "",
      email_permission: false
    }
  });

  const onSubmit = async (data: InterestFormData) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const response = await makeApiCall('/api/v1/member/coaching-interest/', {
        method: 'POST',
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to submit coaching interest');
      }

      setSubmitSuccess(true);
      reset();
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Error submitting coaching interest:', error);
      setSubmitError(error instanceof Error ? error.message : 'Failed to submit coaching interest');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitSuccess) {
    return (
      <Card className="max-w-md mx-auto">
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="p-3 bg-green-100 rounded-full">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Thank you for your interest!
              </h3>
              <p className="text-muted-foreground text-sm">
                We've received your coaching interest form. Our team will review your goals and connect you with a suitable coach soon.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Express Your Interest</CardTitle>
        <CardDescription>
          Tell us about your goals and we'll help connect you with the right coach.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {submitError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{submitError}</p>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="name">Full Name *</Label>
            <Input
              id="name"
              {...register("name")}
              placeholder="Enter your full name"
              disabled={isSubmitting}
              aria-invalid={!!errors.name}
            />
            {errors.name && (
              <p className="text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email Address *</Label>
            <Input
              id="email"
              type="email"
              {...register("email")}
              placeholder="Enter your email address"
              disabled={isSubmitting}
              aria-invalid={!!errors.email}
            />
            {errors.email && (
              <p className="text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="goals">Your Goals *</Label>
            <Textarea
              id="goals"
              {...register("goals")}
              placeholder="Tell us about your goals and what you'd like to achieve through coaching..."
              disabled={isSubmitting}
              className="min-h-[100px] resize-none"
              aria-invalid={!!errors.goals}
            />
            {errors.goals && (
              <p className="text-sm text-red-600">{errors.goals.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-start space-x-2">
              <input
                id="email_permission"
                type="checkbox"
                {...register("email_permission")}
                disabled={isSubmitting}
                className="mt-1 h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              />
              <Label htmlFor="email_permission" className="text-sm leading-5">
                I agree to receive email communications about coaching opportunities and updates. *
              </Label>
            </div>
            {errors.email_permission && (
              <p className="text-sm text-red-600">{errors.email_permission.message}</p>
            )}
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h4 className="text-sm font-medium text-blue-800 mb-1">What happens next?</h4>
            <ul className="text-xs text-blue-700 space-y-1">
              <li>• We'll review your goals and preferences</li>
              <li>• Our team will match you with a suitable coach</li>
              <li>• You'll receive an email with next steps</li>
              <li>• Start your coaching journey!</li>
            </ul>
          </div>

          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Submit Interest
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}