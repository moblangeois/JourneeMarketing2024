import React from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea: React.FC<TextareaProps> = (props) => {
  return (
    <textarea 
      {...props} 
      className={`px-3 py-2 border border-gray-300 rounded-md ${props.className || ''}`}
    />
  );
};