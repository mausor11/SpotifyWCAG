import { useNavigate } from 'react-router-dom';
import React, { useEffect, useState } from 'react';
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

export default function RecentlyPlayed({ currentView, onViewChange }) {
  const navigate = useNavigate();
  const [recentTracks, setRecentTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [track, setTrack] = useState(null);
  const [shuffleOn, setShuffleOn] = useState(false);
  const [repeatState, setRepeatState] = useState('off');

  useEffect(() => {
    fetchRecentTracks();
    fetchTrack();
    fetchPlayerState();
  }, []);

  const fetchRecentTracks = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/recently-played-tracks');
      setRecentTracks(res.data || []);
    } catch (err) {
      console.error('❌ Błąd pobierania ostatnio granych:', err);
      setRecentTracks([]);
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

  const handlePlayTrack = async (trackId) => {
    try {
      await axios.post('http://127.0.0.1:5000/play-single-track', { track_id: trackId });
      await fetchTrack();
    } catch (err) {
      console.error("❌ Błąd przy odtwarzaniu utworu:", err);
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

  const handleSwitchToPlayer = () => {
    navigate('/player');
  };

  const isPlaying = track?.is_playing ?? false;
  const playIcon = isPlaying ? PlayIcon : ResumeIcon;
  const playHoverIcon = isPlaying ? PlayActive : ResumeActive;

  return (
    <div className="recently-played-root" role="main">
      <TopNav currentView={currentView} onViewChange={onViewChange} />
      <div className="recently-played-header">
        <h1>Ostatnio grane</h1>
        <p>Twoje ostatnio odtwarzane utwory</p>
      </div>

      {loading ? (
        <div className="loading-container" role="status" aria-live="polite">
          <div className="loading-spinner" aria-hidden="true"></div>
          <p>Ładowanie ostatnio granych...</p>
        </div>
      ) : (
        <div className="recently-played-tracks" role="list" aria-label="Lista ostatnio granych utworów">
          {recentTracks.length > 0 ? (
            recentTracks.map((trackItem, index) => (
              <div 
                key={trackItem.id || index}
                className="recent-track-item"
                onClick={() => handlePlayTrack(trackItem.id)}
                role="button"
                tabIndex={0}
                aria-label={`Odtwórz ${trackItem.name} - ${trackItem.artist}`}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handlePlayTrack(trackItem.id);
                  }
                }}
              >
                <div className="track-number" aria-label={`Pozycja ${index + 1}`}>{index + 1}</div>
                <img 
                  src={trackItem.image} 
                  alt={`Okładka albumu - ${trackItem.name}`} 
                  className="track-image" 
                />
                <div className="track-info">
                  <div className="track-name">{trackItem.name}</div>
                  <div className="track-artist">{trackItem.artist}</div>
                </div>
                <div className="track-album">{trackItem.album}</div>
                <div className="track-duration" aria-label={`Czas trwania: ${trackItem.duration}`}>{trackItem.duration}</div>
              </div>
            ))
          ) : (
            <div className="no-tracks" role="status" aria-live="polite">
              <p>Brak ostatnio granych utworów</p>
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