const TOPICS = [
  { label: "Tax Rates" },
  { label: "Deductions" },
  { label: "Medicare" },
  { label: "HELP / HECS" },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  onNewChat: () => void;
}

export default function Sidebar({ open, onClose, onNewChat }: SidebarProps) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-[220px] bg-navy-deep flex flex-col
          transition-transform duration-200
          ${open ? "translate-x-0" : "-translate-x-full"}
          md:relative md:translate-x-0 md:flex
        `}
      >
        <div className="px-5 py-5 flex items-center gap-3 border-b border-white/10">
          <div className="w-5 h-5 bg-gold rounded flex-shrink-0" />
          <span className="text-white text-xs font-semibold tracking-widest uppercase">
            ATO Assistant
          </span>
        </div>

        <nav className="flex-1 px-3 py-4">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-gold/60 px-2 mb-2">
            Topics
          </p>
          {TOPICS.map((t) => (
            <button
              key={t.label}
              className="w-full text-left px-3 py-2 rounded text-sm text-[#7fa8cc] hover:bg-navy-mid/40 transition-colors"
            >
              {t.label}
            </button>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-white/10">
          <button
            onClick={onNewChat}
            className="w-full text-left px-3 py-2 rounded text-sm text-[#7fa8cc] hover:bg-navy-mid/40 transition-colors"
          >
            + New chat
          </button>
        </div>
      </aside>
    </>
  );
}
