import * as React from "react"
import { cn } from "@/lib/utils"

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline'
}

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-primary text-primary-foreground hover:bg-primary/90",
    secondary: "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/90",
    destructive: "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/90",
    outline: "text-foreground border-border hover:bg-muted",
  }

  return (
    <div 
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2",
        variants[variant],
        className
      )} 
      {...props} 
    />
  )
}

export { Badge }