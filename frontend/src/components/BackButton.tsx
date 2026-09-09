import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface BackButtonProps {
  to?: string;
  label?: string;
  className?: string;
}

/**
 * Professional back navigation control with glassmorphism styling.
 * 
 * Behavior:
 * - If `to` is provided, navigates to that route
 * - Otherwise uses browser history navigation
 * - Handles edge cases gracefully (no history available)
 */
const BackButton = ({ to, label = 'Back', className = '' }: BackButtonProps) => {
  const navigate = useNavigate();

  const handleBack = () => {
    if (to) {
      // Navigate to specific route (logical parent)
      navigate(to);
    } else {
      // Use browser history
      // Check if there's history to go back to
      if (window.history.state && window.history.state.idx > 0) {
        navigate(-1);
      } else {
        // Fallback to dashboard if no history
        navigate('/dashboard');
      }
    }
  };

  return (
    <button
      onClick={handleBack}
      className={`
        group
        inline-flex items-center space-x-2
        px-3 py-2 rounded-lg
        bg-white/40 backdrop-blur-xl
        border border-white/40
        text-neutral-800 hover:text-neutral-900
        font-medium text-sm
        transition-all duration-200
        hover:bg-white/50
        hover:border-white/50
        hover:shadow-lg
        active:scale-[0.97]
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent
        ${className}
      `}
      style={{ boxShadow: '0 4px 16px -4px rgba(31, 38, 135, 0.15)' }}
      aria-label={`Navigate back to ${label.toLowerCase()}`}
    >
      <ArrowLeft className="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-0.5" />
      <span>{label}</span>
    </button>
  );
};

export default BackButton;
