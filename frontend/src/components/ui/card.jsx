import * as React from 'react';
import { cn } from '../../lib/utils';

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('rounded-lg border bg-card text-card-foreground shadow-sm', className)} {...props} />
));
Card.displayName = 'Card';

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('flex items-center justify-between gap-3 border-b px-4 py-2', className)} {...props} />
));
CardHeader.displayName = 'CardHeader';

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-4', className)} {...props} />
));
CardContent.displayName = 'CardContent';

export { Card, CardContent, CardHeader };

