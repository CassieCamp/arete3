"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface CheckboxProps {
  id?: string
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
  disabled?: boolean
  className?: string
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ id, checked, onCheckedChange, disabled, className, ...props }, ref) => {
    return (
      <input
        type="checkbox"
        id={id}
        ref={ref}
        checked={checked}
        onChange={(e) => onCheckedChange?.(e.target.checked)}
        disabled={disabled}
        className={cn(
          "h-4 w-4 rounded border border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2",
          disabled && "opacity-50 cursor-not-allowed",
          className
        )}
        {...props}
      />
    )
  }
)

Checkbox.displayName = "Checkbox"

export { Checkbox }