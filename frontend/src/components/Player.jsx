import { useEffect, useState, useRef, useLayoutEffect } from 'react'
import { useNavigate } from 'react-router-dom';
import axios from 'axios'
import io from 'socket.io-client'
import '../App.css'

import IconButton from './IconButton'
import ToggleButton from './ToggleButton'
import QueueItem from './QueueItem'

import ResumeIcon from '../icons/resume.svg'
import ResumeActive from '../icons/resume_ac.svg'
import PlayIcon from '../icons/play.svg'
import PlayActive from '../icons/play_ac.svg'

import NextIcon from '../icons/next.svg'
import NextActive from '../icons/next_ac.svg'
import PrevIcon from '../icons/previous.svg'
import PrevActive from '../icons/previous_ac.svg'

import GestureIcon from '../icons/gesture.svg'
import MicIcon from '../icons/microphone.svg'

import ShuffleIcon from '../icons/shuffle.svg'
import ShuffleActive from '../icons/shuffle_ac.svg'
import ShuffleOn from '../icons/shuffle_on.svg'
import ShuffleOnActive from '../icons/shuffle_on_ac.svg'
import RepeatIcon from '../icons/repeat.svg'
import RepeatActive from '../icons/repeat_ac.svg'
import RepeatOn from '../icons/repeat_on.svg'
import RepeatOnActive from '../icons/repeat_on_ac.svg'
import RepeatTrackOn from '../icons/repeat_track_on.svg'
import RepeatTrackOnActive from '../icons/repeat_on_track_ac.svg'
import QueueIcon from '../icons/queue.svg'
import QueueActive from '../icons/queue_ac.svg'

export default function Player() {
  const [track, setTrack] = useState(null)
  const [isScrolled, setIsScrolled] = useState(false)
  const [queueData, setQueueData] = useState(null)
  const [previousTrackId, setPreviousTrackId] = useState(null)

  const [gestureOn, setGestureOn] = useState(false)
  const [micOn, setMicOn] = useState(false)
  const [speechSocket, setSpeechSocket] = useState(null)

  const [volume, setVolume] = useState(50)

  const [shuffleOn, setShuffleOn] = useState(false)
  const [repeatState, setRepeatState] = useState('off')
  const [artistAlbums, setArtistAlbums] = useState([])

  const navigate = useNavigate();

  const handleVolumeChange = async (e) => {
    const newVolume = parseInt(e.target.value)
    setVolume(newVolume)

    try {
      await axios.put(`http://127.0.0.1:5000/set-volume?volume_percent=${newVolume}`)
    } catch (err) {
      console.error("❌ Błąd ustawiania głośności:", err)
    }
  }

  const fetchPlayerState = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/player-state')
      if (res.data) {
        setShuffleOn(res.data.shuffle_state)
        setRepeatState(res.data.repeat_state || 'off')
      }
    } catch (err) {
      console.error('❌ Błąd pobierania stanu shuffle/repeat:', err)
    }
  }

  const fetchTrack = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/current-track')
      if (res.status === 204 || !res.data) {
        setTrack(null)
        setPreviousTrackId(null)
        return
      }
      
      const newTrack = res.data
      const currentTrackId = newTrack.track_id || `${newTrack.track}-${newTrack.artist}` // Fallback jeśli brak track_id
      
      const trackChanged = previousTrackId !== currentTrackId
      
      setTrack(newTrack)
      setPreviousTrackId(currentTrackId)
      
      if (trackChanged) {
        console.log("🔄 Utwór się zmienił, aktualizuję kolejkę...", { 
          previous: previousTrackId, 
          current: currentTrackId,
          trackName: newTrack.track 
        })
        await fetchQueue()
      } else {
        console.log("⏭️ Utwór się nie zmienił, pomijam aktualizację kolejki", { 
          trackId: currentTrackId,
          trackName: newTrack.track 
        })
      }
      
      await fetchPlayerState()
    } catch (err) {
      console.error("❌ Błąd połączenia z backendem:", err)
      setTrack(null)
      setPreviousTrackId(null)
    }
  }

  const fetchQueue = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/queue');
      if (res.data) {
        setQueueData(res.data);
      } else {
        setQueueData(null);
      }
    } catch (err) {
      console.error("❌ Błąd pobierania kolejki:", err);
      setQueueData(null);
    }
  };

  const handlePlayTrack = async (trackIndex) => {
    if (!queueData || !queueData.queue || queueData.queue.length === 0) return;
    
    // Tworzymy listę URI od klikniętego utworu do końca
    const urisToPlay = queueData.queue.slice(trackIndex).map(track => track.uri);

    try {
      await axios.post('http://127.0.0.1:5000/play-track', { uris: urisToPlay });
      // Odświeżamy dane natychmiast po wysłaniu żądania
      await fetchTrack(); // fetchTrack już sprawdza czy utwór się zmienił i aktualizuje kolejkę
    } catch (err) {
      console.error("❌ Błąd przy odtwarzaniu utworu z kolejki:", err);
    }
  };

  const handlePlayAlbum = async (albumId) => {
    try {
      await axios.post('http://127.0.0.1:5000/play-album', { album_id: albumId });
      // Odświeżamy dane po odtworzeniu albumu
      await fetchTrack();
    } catch (err) {
      console.error("❌ Błąd przy odtwarzaniu albumu:", err);
    }
  };

  useEffect(() => {
    fetchTrack()
    fetchQueue()
    const interval = setInterval(() => {
      fetchTrack()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  // WebSocket connection dla gestów
  useEffect(() => {
    const socket = io('http://127.0.0.1:5001');
    
    socket.on('connect', () => {
      console.log('🔌 Połączono z serwerem gestów');
    });
    
    socket.on('disconnect', () => {
      console.log('🔌 Rozłączono z serwerem gestów');
    });
    
    socket.on('spotify_action', (data) => {
      console.log(`🎵 Akcja Spotify z gestów: ${data.action} - ${data.message}`);
      handleSpotifyAction(data);
    });
    
    return () => {
      socket.close();
    };
  }, []);

  // Cleanup dla socketów przy odmontowaniu komponentu
  useEffect(() => {
    return () => {
      if (speechSocket) {
        speechSocket.disconnect();
      }
    };
  }, [speechSocket]);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const sendControl = async (endpoint) => {
    try {
      if (endpoint === 'play') {
        setTrack(prev => prev ? { ...prev, is_playing: !prev.is_playing } : prev)
      }

      await axios.post(`http://127.0.0.1:5000/${endpoint}`)
      
      // Dodajemy małe opóźnienie dla next/previous, żeby Spotify API miał czas na zaktualizowanie stanu
      if (endpoint === 'next' || endpoint === 'previous') {
        setTimeout(() => {
          fetchTrack() // odśwież dane po akcji
        }, 500)
      } else {
        fetchTrack() // odśwież dane po akcji
      }
    } catch (err) {
      console.error(`❌ Błąd przy ${endpoint}:`, err)
    }
  }

  const handleShuffleClick = async () => {
    try {
      await axios.put(`http://127.0.0.1:5000/set-shuffle?state=${!shuffleOn}`)
      setShuffleOn(!shuffleOn)
    } catch (err) {
      console.error('❌ Błąd ustawiania shuffle:', err)
    }
  }

  const handleRepeatClick = async () => {
    try {
      let newState = 'off'
      if (repeatState === 'off') newState = 'context'
      else if (repeatState === 'context') newState = 'track'
      else if (repeatState === 'track') newState = 'off'
      await axios.put(`http://127.0.0.1:5000/set-repeat?state=${newState}`)
      setRepeatState(newState)
    } catch (err) {
      console.error('❌ Błąd ustawiania repeat:', err)
    }
  }

  const handleSpotifyAction = (actionData) => {
    console.log('🎵 Akcja Spotify z gestów:', actionData);
    // Odśwież stan odtwarzania po akcji gestu
    setTimeout(() => {
      fetchTrack();
    }, 500);
  }

  const handleGestureToggle = async () => {
    const newState = !gestureOn;
    setGestureOn(newState);
    
    try {
      const response = await fetch('http://127.0.0.1:5001/gestures/toggle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enable: newState }),
      });
      
      const data = await response.json();
      console.log(`🎯 ${data.message}`);
    } catch (error) {
      console.error('❌ Błąd przełączania gestów:', error);
      setGestureOn(!newState); // Cofnij stan w przypadku błędu
    }
  }

  const handleMicToggle = async () => {
    const newMicState = !micOn
    setMicOn(newMicState)
    
    try {
      if (newMicState) {
        // Połącz z serwerem mowy
        const socket = io('http://127.0.0.1:5002')
        setSpeechSocket(socket)
        
        socket.on('connect', () => {
          console.log('🎤 Połączono z serwerem mowy')
          socket.emit('start_speech')
        })
        
        socket.on('speech_command', (data) => {
          console.log('🎤 Komenda głosowa:', data)
          handleSpeechCommand(data)
        })
        
        socket.on('speech_status', (data) => {
          console.log('🎤 Status mowy:', data)
        })
        
      } else {
        // Rozłącz z serwerem mowy
        if (speechSocket) {
          speechSocket.emit('stop_speech')
          speechSocket.disconnect()
          setSpeechSocket(null)
          console.log('🛑 Rozpoznawanie mowy wyłączone')
        }
      }
    } catch (err) {
      console.error('❌ Błąd połączenia z serwerem mowy:', err)
    }
  }

  const handleSpeechCommand = async (commandData) => {
    try {
      const { action, song } = commandData
      
      switch (action) {
        case 'next':
          await sendControl('next')
          console.log('🎵 Następny utwór (głos)')
          break
        case 'previous':
          await sendControl('previous')
          console.log('🎵 Poprzedni utwór (głos)')
          break
        case 'play':
        case 'pause':
          await sendControl('play')
          console.log('🎵 Play/Pause (głos)')
          break
        case 'play_song':
          if (song) {
            console.log(`🎵 Próba odtworzenia: ${song}`)
            try {
              const response = await axios.post('http://127.0.0.1:5000/speech-command', {
                action: 'play_song',
                song: song
              })
              if (response.data.success) {
                console.log(`✅ ${response.data.message}`)
                // Odśwież dane po odtworzeniu
                setTimeout(() => fetchTrack(), 1000)
              } else {
                console.log(`❌ ${response.data.message}`)
              }
            } catch (err) {
              console.error('❌ Błąd odtwarzania piosenki:', err)
            }
          }
          break
        default:
          console.log('❌ Nieznana komenda głosowa:', action)
      }
    } catch (err) {
      console.error('❌ Błąd wykonania komendy głosowej:', err)
    }
  }

  const wrapperRef = useRef(null);
  const marqueeRef = useRef(null);
  const [offset, setOffset] = useState(0);

  const formatDuration = (durationMs) => {
    if (!durationMs) return "0:00";
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  useLayoutEffect(() => {
    if (wrapperRef.current && marqueeRef.current) {
      const wrapperWidth = wrapperRef.current.offsetWidth;
      const marqueeWidth = marqueeRef.current.scrollWidth;

      const contentWidth = wrapperWidth - 40;
      const distance = marqueeWidth - contentWidth;
      
      setOffset(distance > 0 ? distance : 0);
    }
  }, [track])

  const fetchArtistAlbums = async (artistId) => {
    if (!artistId) return;
    try {
      const res = await axios.get(`http://127.0.0.1:5000/artist-albums/${artistId}`);
      setArtistAlbums(res.data);
    } catch (err) {
      console.error("❌ Błąd pobierania albumów artysty:", err);
      setArtistAlbums([]);
    }
  };

  useEffect(() => {
    if (track && track.artist_id) {
      fetchArtistAlbums(track.artist_id);
    }
  }, [track?.artist_id]); // Uruchom, gdy zmieni się ID artysty

  if (!track) {
    return (
      <main className="player-container" role="main">
        <div className="wrapper">
          <p aria-live="polite">Brak aktywnego utworu lub połączenia z backendem</p>
        </div>
      </main>
    )
  }
  const shouldScroll = offset > 0

  const isPlaying = track?.is_playing ?? false
  const playIcon = isPlaying ? PlayIcon : ResumeIcon
  const playHoverIcon = isPlaying ? PlayActive : ResumeActive

  console.log("Renderowanie komponentu, stan queueData:", queueData);

  return (
    <div className="app-wrapper">
      <div
        className="background-blur"
        style={{ backgroundImage: `url(${track.image})` }}
      />
      <div className="background-gradient" />

      <header className={`top-controls ${isScrolled ? 'scrolled' : ''}`}>
        <div className="top-controls-content">
          <div className="top-controls-left">
            <button type="button" className="top-button left" aria-label="Wyjście do menu głównego" onClick={() => navigate('/')}>
              <span className="icon" aria-hidden="true">🔉</span> Exit
            </button>
          </div>

          <div className="volume-slider">
            <label htmlFor="volume-control" className="sr-only">Głośność</label>
            <input
              id="volume-control"
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={handleVolumeChange}
              aria-label={`Głośność: ${volume}%`}
              className="volume-range"
            />
            <div className="volume-track" aria-hidden="true">
              <div className="volume-fill" style={{ width: `${volume}%` }}></div>
              <div className="volume-icon">🔊</div>
            </div>
          </div>
          
          <div className="right-buttons">
            <ToggleButton
              icon={GestureIcon}
              label={'Gesty\u00A0\u00A0\u00A0\u00A0'}
              isActive={gestureOn}
              aria-pressed={gestureOn}
              onClick={handleGestureToggle}
            />
            <ToggleButton
              icon={MicIcon}
              label="Mikrofon"
              isActive={micOn}
              aria-pressed={micOn}
              onClick={handleMicToggle}
            />
          </div>
        </div>
      </header>

      <main>
        <div className="player-container">
          <div className="wrapper">
            <img src={track.image} alt="" aria-hidden="true" className="album-img" />
            <h1 className={`track-title ${shouldScroll ? 'is-scrolling' : ''}`} ref={wrapperRef}>
              <span
                className="marquee"
                ref={marqueeRef}
                style={{
                  animation: shouldScroll
                    ? `scroll-back-and-forth 20s ease-in-out infinite`
                    : 'none',
                  '--scroll-distance': `-${offset}px`
                }}
              >
                {track.track}
              </span>
            </h1>

            <h2 className="artist-label">{track.artist}</h2>
          </div>
        </div>

        <div className="queue-container">
          <h2 className="queue-title">Kolejka</h2>
          <div className="queue-list" role="list" aria-label="Lista utworów w kolejce">
            {queueData && queueData.queue && queueData.queue.length > 0 ? (
              queueData.queue.slice(0, 10).map((queueTrack, index) => (
                <QueueItem 
                  key={queueTrack.id || index}
                  track={queueTrack} 
                  index={index}
                  onPlay={handlePlayTrack}
                  trackImage={track.image}
                />
              ))
            ) : (
              <div className="queue-item is-visible" role="listitem">
                <div className="queue-item-info">
                  <div className="queue-item-title">Kolejka jest pusta</div>
                  <div className="queue-item-artist">Dodaj utwory do kolejki w aplikacji Spotify</div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="showcase-container">
          {/* Lewa strona - duża karta artysty */}
          {track && track.artist_image && (
            <div className="featured-artist-card">
              <img src={track.artist_image} alt={`Zdjęcie artysty - ${track.artist_main}`} className="featured-artist-img" />
              <div className="featured-artist-gradient" aria-hidden="true"></div>
              <div className="featured-artist-info">
                <div className="featured-artist-title">{track.artist_main}</div>
                <div className="featured-artist-subtitle">Artysta</div>
              </div>
            </div>
          )}

          {/* Prawa strona - siatka albumów */}
          <div className="album-grid-container">
            <h2 className="album-grid-title">Albumy</h2>
            <div className="album-grid" role="grid" aria-label="Albumy artysty">
              {artistAlbums.map(album => (
                <div 
                  className="album-card" 
                  key={album.id}
                  onClick={() => handlePlayAlbum(album.id)}
                  role="button"
                  tabIndex={0}
                  aria-label={`Odtwórz album ${album.name}`}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handlePlayAlbum(album.id);
                    }
                  }}
                >
                  <img src={album.images?.[0]?.url} alt={`Okładka - ${album.name}`} className="album-card-img" />
                  <div className="album-card-title">{album.name}</div>
                  <div className="album-card-subtitle">{album.album_type === 'single' ? 'Singiel' : 'Album'}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      <footer className={`controls-row ${isScrolled ? 'scrolled' : ''}`} role="contentinfo">
        <div className="now-playing-bar">
          <img src={track.image} alt="" className="now-playing-art" aria-hidden="true" />
          <div className="now-playing-info">
            <div className="now-playing-title">{track.track}</div>
            <div className="now-playing-artist">{track.artist}</div>
          </div>
        </div>
        <div className="controls" role="group" aria-label="Kontrolki odtwarzania">
          <IconButton
            onClick={handleShuffleClick}
            defaultIcon={shuffleOn ? ShuffleOn : ShuffleIcon}
            hoverIcon={shuffleOn ? ShuffleOnActive : ShuffleActive}
            alt={shuffleOn ? 'Wyłącz losowe odtwarzanie' : 'Włącz losowe odtwarzanie'}
          />
          <IconButton
            onClick={() => sendControl('previous')}
            defaultIcon={PrevIcon}
            hoverIcon={PrevActive}
            alt="Poprzedni utwór"
          />
          <IconButton
            onClick={() => sendControl('play')}
            defaultIcon={playIcon}
            hoverIcon={playHoverIcon}
            alt={isPlaying ? 'Wstrzymaj utwór' : 'Graj utwór'}
          />
          <IconButton
            onClick={() => sendControl('next')}
            defaultIcon={NextIcon}
            hoverIcon={NextActive}
            alt="Następny utwór"
          />
          <IconButton
            onClick={handleRepeatClick}
            defaultIcon={
              repeatState === 'track' ? RepeatTrackOn : (repeatState !== 'off' ? RepeatOn : RepeatIcon)
            }
            hoverIcon={
              repeatState === 'track' ? RepeatTrackOnActive : (repeatState !== 'off' ? RepeatOnActive : RepeatActive)
            }
            alt={
              repeatState === 'off' ? 'Włącz powtarzanie playlisty' :
              repeatState === 'context' ? 'Włącz powtarzanie utworu' :
              'Wyłącz powtarzanie'
            }
          />
        </div>
        <div className="controls-placeholder" />
      </footer>
    </div>
  )
} 