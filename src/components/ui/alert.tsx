import React from 'react';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive';
}

export const Alert: React.FC<AlertProps> = ({ children, variant = 'default', ...props }) => {
  const baseStyle = 'p-4 rounded-md';
  const variantStyles = {
    default: 'bg-blue-100 text-blue-800 border border-blue-300',
    destructive: 'bg-red-100 text-red-800 border border-red-300'
  };

  return (
    <div 
      role="alert"
      {...props} 
      className={`${baseStyle} ${variantStyles[variant]} ${props.className || ''}`}
    >
      {children}
    </div>
  );
};

export const AlertDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ children, ...props }) => {
  return (
    <p {...props} className={`mt-2 text-sm ${props.className || ''}`}>
      {children}
    </p>
  );
};