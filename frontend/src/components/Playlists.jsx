import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import TopNav from './TopNav';
import IconButton from './IconButton';

// Import ikon dla kontroli odtwarzania
import ResumeIcon from '../icons/resume.svg'
import ResumeActive from '../icons/resume_ac.svg'
import PlayIcon from '../icons/play.svg'
import PlayActive from '../icons/play_ac.svg'
import NextIcon from '../icons/next.svg'
import NextActive from '../icons/next_ac.svg'
import PrevIcon from '../icons/previous.svg'
import PrevActive from '../icons/previous_ac.svg'
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

function chunkArray(array, size) {
  const result = [];
  for (let i = 0; i < array.length; i += size) {
    result.push(array.slice(i, i + size));
  }
  return result;
}

export default function Playlists({ currentView, onViewChange }) {
  const navigate = useNavigate();
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [track, setTrack] = useState(null);
  const [shuffleOn, setShuffleOn] = useState(false);
  const [repeatState, setRepeatState] = useState('off');

  useEffect(() => {
    fetchPlaylists();
    fetchTrack();
    fetchPlayerState();
  }, []);

  const fetchPlaylists = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/user-playlists?limit=50');
      setPlaylists(res.data || []);
    } catch (err) {
      console.error('❌ Błąd pobierania playlist:', err);
      setPlaylists([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrack = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/current-track');
      if (res.status === 204 || !res.data) {
        setTrack(null);
        return;
      }
      setTrack(res.data);
    } catch (err) {
      console.error("❌ Błąd połączenia z backendem:", err);
      setTrack(null);
    }
  };

  const fetchPlayerState = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/player-state');
      if (res.data) {
        setShuffleOn(res.data.shuffle_state);
        setRepeatState(res.data.repeat_state || 'off');
      }
    } catch (err) {
      console.error('❌ Błąd pobierania stanu shuffle/repeat:', err);
    }
  };
  const handleSwitchToPlayer = () => {
    navigate('/player');
  };

  const handlePlayPlaylist = async (playlistId) => {
    try {
      await axios.post('http://127.0.0.1:5000/play-playlist', { playlist_id: playlistId });
      navigate('/player');
    } catch (err) {
      console.error("❌ Błąd przy odtwarzaniu playlisty:", err);
    }
  };

  const sendControl = async (endpoint) => {
    try {
      if (endpoint === 'play') {
        setTrack(prev => prev ? { ...prev, is_playing: !prev.is_playing } : prev);
      }

      await axios.post(`http://127.0.0.1:5000/${endpoint}`);
    } catch (err) {
      console.error(`❌ Błąd przy ${endpoint}:`, err);
    }
  };

  const handleShuffleClick = async () => {
    try {
      await axios.put(`http://127.0.0.1:5000/set-shuffle?state=${!shuffleOn}`);
      setShuffleOn(!shuffleOn);
    } catch (err) {
      console.error('❌ Błąd ustawiania shuffle:', err);
    }
  };

  const handleRepeatClick = async () => {
    try {
      let newState = 'off';
      if (repeatState === 'off') newState = 'context';
      else if (repeatState === 'context') newState = 'track';
      else if (repeatState === 'track') newState = 'off';
      await axios.put(`http://127.0.0.1:5000/set-repeat?state=${newState}`);
      setRepeatState(newState);
    } catch (err) {
      console.error('❌ Błąd ustawiania repeat:', err);
    }
  };

  const playlistRows = chunkArray(playlists, 3);
  const isPlaying = track?.is_playing ?? false;
  const playIcon = isPlaying ? PlayIcon : ResumeIcon;
  const playHoverIcon = isPlaying ? PlayActive : ResumeActive;

  return (
    <div className="playlists-root" role="main">
      <TopNav currentView={currentView} onViewChange={onViewChange} />
      
      <div className="albums-header">
        <h1>Twoje playlisty</h1>
        <p>Wszystkie playlisty z Twojej biblioteki</p>
      </div>

      {loading ? (
        <div className="loading-container" role="status" aria-live="polite">
          <div className="loading-spinner" aria-hidden="true"></div>
          <p>Ładowanie playlist...</p>
        </div>
      ) : (
        <div className="albums-content">
          {playlists.length > 0 ? (
            playlistRows.map((row, rowIndex) => (
              <div className="homepage-album-row" key={rowIndex} role="list" aria-label="Playlisty z biblioteki">
                {row.map(playlist => (
                  <div 
                    className="homepage-album-card" 
                    key={playlist.id}
                            onClick={() => handlePlayPlaylist(playlist.id)}
                    role="button"
                    tabIndex={0}
                    aria-label={`Odtwórz playlist ${playlist.name}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handlePlayPlaylist(playlist.id);
                      }
                    }}
                  >
                    <img src={playlist.image} alt={`Okładka playlisty ${playlist.name}`} className="homepage-album-img" />
                    <div className="homepage-album-title">{playlist.name}</div>
                    <div className="homepage-album-author">{playlist.author}</div>
                  </div>
                ))}
              </div>
            ))
          ) : (
            <div className="no-albums" role="status" aria-live="polite">
              <p>Brak playlist w bibliotece</p>
            </div>
          )}
        </div>
      )}

      {/* Pasek kontrolny na dole */}
      {track && (
        <footer className="controls-row scrolled" role="contentinfo">
          <div className="now-playing-bar">
            <img src={track.image} alt="" className="now-playing-art" aria-hidden="true" />
            <div className="now-playing-info">
            <div className="now-playing-title"
              onClick={handleSwitchToPlayer}
              role="button"
              tabIndex={0}
              aria-label={`Odtwórz utwór ${track.track}`}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleSwitchToPlayer();
                }
              }}
              style={{ cursor: 'pointer' }}
              >{track.track}</div>
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
      )}
    </div>
  );
} 