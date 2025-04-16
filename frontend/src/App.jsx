import { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import './App.css'

import ResumeIcon from './icons/resume.svg'
import ResumeActive from './icons/resume_ac.svg'
import PlayIcon from './icons/play.svg'
import PlayActive from './icons/play_ac.svg'

import NextIcon from './icons/next.svg'
import NextActive from './icons/next_ac.svg'
import PrevIcon from './icons/previous.svg'
import PrevActive from './icons/previous_ac.svg'

function IconButton({ onClick, defaultIcon, hoverIcon, alt }) {
  const [hover, setHover] = useState(false)

  return (
    <button
      className="control-button"
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      aria-label={alt}
    >
      <img src={hover ? hoverIcon : defaultIcon} alt={alt} />
    </button>
  )
}


export default function App() {
  const [track, setTrack] = useState(null)
  const [hovered, setHovered] = useState(false)



  const fetchTrack = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/current-track')

      if (res.status === 204 || !res.data) {
        setTrack(null)
        return
      }

      setTrack(res.data)
    } catch (err) {
      console.error("❌ Błąd połączenia z backendem:", err)
      setTrack(null)
    }
  }

  useEffect(() => {
    fetchTrack()
    const interval = setInterval(fetchTrack, 5000)
    return () => clearInterval(interval)
  }, [])

  const sendControl = async (endpoint) => {
  try {
    await axios.post(`http://127.0.0.1:5000/${endpoint}`)
    fetchTrack() // odśwież dane po akcji
    } catch (err) {
      console.error(`❌ Błąd przy ${endpoint}:`, err)
    }
  }


  const wrapperRef = useRef(null);
  const marqueeRef = useRef(null);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    if (wrapperRef.current && marqueeRef.current) {
      const wrapperWidth = wrapperRef.current.offsetWidth;
      const marqueeWidth = marqueeRef.current.scrollWidth;

      const distance = marqueeWidth - wrapperWidth;
      setOffset(distance > 0 ? distance : 0);
    }
  }, [track])


  if (!track) {
    return (
      <main className="container" role="main">
        <div className="wrapper">
          <p aria-live="polite">Brak aktywnego utworu lub połączenia z backendem</p>
        </div>
      </main>

    )
  }
  const shouldScroll = track.track.length > 15

  const isPlaying = track?.is_playing ?? false
  const playIcon = isPlaying ? PlayIcon : ResumeIcon
  const playHoverIcon = isPlaying ? PlayActive : ResumeActive



  return (
    <div className="container">
      <h1 className="sr-only">Spotify – odtwarzacz muzyczny</h1>
      <div
      className="background-blur"
      style={{ backgroundImage: `url(${track.image})` }}
      />
      <div
        className="background-gradient"
        />
      <div className="top-controls">
        <button className="top-button left" aria-label="Wyjście do menu głównego">
          <span className="icon">🔉</span> Exit
        </button>
        <div className="right-buttons">
          <button className="top-button gesture on" aria-label="Gesty włączone">Gesture On</button>
          <button className="top-button" aria-label="Sterowanie głosem włączone">Use Microphone</button>
        </div>
      </div>

      <div
        className="volume-slider"
        role="slider"
        tabIndex="0"
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow="50"
        aria-label="Głośność: 50%"
      >
        <div className="volume-track">
          <div className="volume-fill" style={{ width: '50%' }}></div>
          <div className="volume-icon">🔊</div>
        </div>
      </div>


      <div className="wrapper">
        <img src={track.image} alt="" aria-hidden="true" className="album-img" />
        <h1 className="track-title" ref={wrapperRef}>
          <span
            className="marquee"
            ref={marqueeRef}
            style={{
              animation: shouldScroll
                ? `scroll-custom 8s linear infinite`
                : 'none',
              '--scroll-distance': `-${offset}px`
            }}
          >
            {track.track}
          </span>
        </h1>


        <h2 className="artist-label">{track.artist}</h2>

        <div className="controls">
          <IconButton
            onClick={() => sendControl('previous')}
            defaultIcon={PrevIcon}
            hoverIcon={PrevActive}
            alt="Previous"
          />
          <IconButton
            onClick={() => sendControl('play')}
            defaultIcon={playIcon}
            hoverIcon={playHoverIcon}
            alt={isPlaying ? 'Pause' : 'Play'}
          />
          <IconButton
            onClick={() => sendControl('next')}
            defaultIcon={NextIcon}
            hoverIcon={NextActive}
            alt="Next"
          />
        </div>

      </div>
    </div>
  )
}
