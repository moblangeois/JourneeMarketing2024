import React from 'react';

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, ...props }) => {
  return (
    <div {...props} className={`bg-white shadow-md rounded-lg ${props.className || ''}`}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, ...props }) => {
  return (
    <div {...props} className={`px-6 py-4 border-b ${props.className || ''}`}>
      {children}
    </div>
  );
};

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ children, ...props }) => {
  return (
    <h3 {...props} className={`text-lg font-semibold ${props.className || ''}`}>
      {children}
    </h3>
  );
};

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, ...props }) => {
  return (
    <div {...props} className={`px-6 py-4 ${props.className || ''}`}>
      {children}
    </div>
  );
};