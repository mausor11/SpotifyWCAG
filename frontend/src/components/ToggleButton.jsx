export default function ToggleButton({ icon, label, isActive, onClick }) {
  return (
    <button
      className={`top-button toggle-button ${isActive ? 'on' : ''}`}
      onClick={onClick}
      aria-pressed={isActive}
    >
      <img src={icon} alt="" className="icon" />
      <div className="toggle-labels">
        <span className="main-label">{label}</span>
        <span className="sub-label">{isActive ? 'Włączone' : 'Wyłączone'}</span>
      </div>
    </button>
  )
}
