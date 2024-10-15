import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'default' | 'outline';
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'default', 
  className, 
  icon,
  ...props 
}) => {
  const baseStyle = 'flex items-center justify-center w-full px-4 py-3 rounded-md transition-all duration-200 font-semibold text-sm';
  const variantStyles = {
    default: 'bg-[#0f172a] text-white hover:bg-[#1e293b]',
    outline: 'border border-[#0f172a] text-[#0f172a] hover:bg-[#f1f5f9]'
  };

  return (
    <button 
      {...props} 
      className={`${baseStyle} ${variantStyles[variant]} ${className || ''}`}
    >
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
};