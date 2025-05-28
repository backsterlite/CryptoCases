import React, { useState } from 'react';

/**
 * DetailsAccordion component provides a collapsible section with a header.
 * @param {object} props
 * @param {string} props.title - The title shown on the accordion header.
 * @param {React.ReactNode} props.children - The content to show inside the accordion panel.
 */
export default function DetailsAccordion({ title, children }) {
  const [isOpen, setIsOpen] = useState(false);

  const toggle = () => {
    setIsOpen(prev => !prev);
  };

  return (
    <div className="border rounded-md overflow-hidden">
      <button
        type="button"
        onClick={toggle}
        className="w-full flex justify-between items-center p-4 bg-gray-100 hover:bg-gray-200 focus:outline-none"
        aria-expanded={isOpen}
      >
        <span className="font-medium text-left">{title}</span>
        <svg
          className={`w-5 h-5 transform transition-transform duration-200 ${isOpen ? 'rotate-180' : 'rotate-0'}`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
      {isOpen && (
        <div className="p-4 bg-white border-t">
          {children}
        </div>
      )}
    </div>
  );
}
