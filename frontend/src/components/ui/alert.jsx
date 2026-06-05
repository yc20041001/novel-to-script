import * as React from 'react';
import { AlertCircle, Info } from 'lucide-react';
import { cn } from '../../lib/utils';

function Alert({ className, variant = 'info', children, ...props }) {
  const Icon = variant === 'warning' ? AlertCircle : Info;
  return (
    <div
      className={cn(
        'flex gap-3 rounded-md border px-3 py-2 text-sm',
        variant === 'warning'
          ? 'border-amber-200 bg-amber-50 text-amber-800'
          : 'border-blue-200 bg-blue-50 text-blue-800',
        className,
      )}
      {...props}
    >
      <Icon className="mt-0.5 h-4 w-4 flex-none" />
      <div>{children}</div>
    </div>
  );
}

export { Alert };

