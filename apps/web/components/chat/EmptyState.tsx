const SUGGESTIONS = [
  "How do I claim work-from-home deductions?",
  "What is the Medicare levy surcharge?",
  "How does the CGT discount work for assets held over 12 months?",
  "Do I need to register for GST as a sole trader?",
  "How are crypto assets taxed in Australia?",
  "What can rideshare drivers claim as deductions?",
  "How does salary sacrificing into super reduce my tax?",
  "What is the HELP repayment threshold for 2024-25?",
];

interface EmptyStateProps {
  onSuggestionClick: (text: string) => void;
}

export default function EmptyState({ onSuggestionClick }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center flex-1 px-4 md:px-6 py-12 md:py-16 text-center">
      <h2 className="text-xl font-semibold text-navy mb-2">
        What would you like to know about Australian tax?
      </h2>
      <p className="text-sm text-gray-500 mb-8">
        Ask anything about individual tax — rates, deductions, Medicare,
        HELP/HECS.
      </p>
      <div className="flex flex-wrap gap-2 justify-center max-w-lg">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSuggestionClick(s)}
            className="border border-chat-border rounded-full px-4 py-2 text-sm text-navy hover:bg-page-bg cursor-pointer transition-colors"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
