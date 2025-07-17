import { useState } from 'react'

export default function IconButton({ onClick, defaultIcon, hoverIcon, alt, className }) {
  const [hover, setHover] = useState(false)

  return (
    <button
      className={`control-button ${className || ''}`}
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      aria-label={alt}
    >
      <img src={hover ? hoverIcon : defaultIcon} alt={alt} />
    </button>
  )
}
