import { useState } from "react";
import { motion } from "motion/react";
import { Send } from "lucide-react";

interface TextInputFallbackProps {
  onSubmit: (text: string) => void;
  disabled?: boolean;
}

export default function TextInputFallback({ onSubmit, disabled }: TextInputFallbackProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSubmit(input);
      setInput("");
    }
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="w-full max-w-2xl"
    >
      <div className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question about wine..."
          disabled={disabled}
          className="w-full px-6 py-4 pr-14 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40 transition-all disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all"
        >
          <Send className="w-4 h-4 text-white" />
        </button>
      </div>
    </motion.form>
  );
}
