export default function VajraMark({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" fill="none" className={className} aria-hidden="true">
      <ellipse cx="32" cy="30" rx="26" ry="10" stroke="#0A0F1E" strokeOpacity="0.18" strokeWidth="1.5" />
      <ellipse cx="32" cy="30" rx="20" ry="7.5" stroke="#0A0F1E" strokeOpacity="0.28" strokeWidth="1.2" />
      <path d="M10 22 L28 52 L32 44 L36 52 L54 22 L44 22 L32 42 L20 22 Z" fill="#0A0F1E" />
      <path d="M32 4 L35 26 L32 30 L29 26 Z" fill="#0A0F1E" />
      <path d="M32 4 L35 26 L32 30 Z" fill="#3A4356" />
    </svg>
  );
}
