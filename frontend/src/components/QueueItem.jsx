import { useState, useEffect, useRef } from 'react';

function QueueItem({ track, index, onPlay, trackImage }) {
  const [isVisible, setIsVisible] = useState(false);
  const itemRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        // Przełączaj stan widoczności w zależności od tego, czy element jest w viewport
        setIsVisible(entry.isIntersecting);
      },
      {
        root: null,
        rootMargin: '0px',
        threshold: 0.1, // Trigger when 10% of the item is visible
      }
    );

    const currentRef = itemRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, []);

  const formatDuration = (durationMs) => {
    if (!durationMs) return '0:00';
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const imageUrl = track.album?.images?.[0]?.url || trackImage;
  const trackName = track.name || 'Nieznany utwór';
  const artistName = track.artists?.map((artist) => artist.name).join(', ') || 'Nieznany artysta';

  return (
    <div
      ref={itemRef}
      className={`queue-item ${isVisible ? 'is-visible' : ''}`}
      style={{ transitionDelay: `${Math.min(index * 50, 500)}ms` }}
      key={track.id || index}
      onClick={() => onPlay(index)}
      role="button"
      tabIndex="0"
      onKeyDown={(e) => {
        if (e.key === 'Enter') onPlay(index);
      }}
    >
      <img src={imageUrl} alt={`Okładka albumu - ${trackName}`} className="queue-item-art" />
      <div className="queue-item-info">
        <div className="queue-item-title">{trackName}</div>
        <div className="queue-item-artist">{artistName}</div>
      </div>
      <div className="queue-item-duration">{formatDuration(track.duration_ms)}</div>
    </div>
  );
}

export default QueueItem; 