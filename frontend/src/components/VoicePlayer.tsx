import React, { useState, useEffect, useRef } from 'react';
import { Volume2, VolumeX, Play, Pause, Square, AlertCircle } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { DecisionCard } from '../types/api';

interface VoicePlayerProps {
  decision: DecisionCard;
}

export const VoicePlayer: React.FC<VoicePlayerProps> = ({ decision }) => {
  const { language, t } = useLanguage();
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [voiceNotice, setVoiceNotice] = useState<string | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Stop speech when unmounted or when decision/language changes
  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [decision.decision_id, language]);

  const handlePlay = () => {
    if (!('speechSynthesis' in window)) {
      setVoiceNotice('Browser does not support text-to-speech.');
      return;
    }

    setVoiceNotice(null);

    // Resume if paused
    if (isPaused) {
      window.speechSynthesis.resume();
      setIsPlaying(true);
      setIsPaused(false);
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    // Resolve vernacular content
    const trans = decision.translations?.[language];
    const action = trans?.primary_action || decision.primary_action;
    const prohibition = trans?.critical_prohibition || decision.critical_prohibition;
    const rationale = trans?.scientific_rationale || decision.scientific_rationale;

    const fullTextToRead = `${action}. ${prohibition}. ${rationale}`;

    const utterance = new SpeechSynthesisUtterance(fullTextToRead);
    utteranceRef.current = utterance;

    // Set voice language code
    const langCode = language === 'mr' ? 'mr-IN' : (language === 'hi' ? 'hi-IN' : 'en-IN');
    utterance.lang = langCode;
    utterance.rate = 0.9; // Slightly slower for clear farmer understanding
    utterance.pitch = 1.0;

    // Check available voices on device
    const availableVoices = window.speechSynthesis.getVoices();
    const matchingVoice = availableVoices.find(
      (v) => v.lang === langCode || v.lang.startsWith(language)
    );

    if (matchingVoice) {
      utterance.voice = matchingVoice;
    } else if (language !== 'en') {
      // Friendly warning if regional TTS voice pack is absent on device
      setVoiceNotice(t.voiceNotAvailable);
    }

    utterance.onend = () => {
      setIsPlaying(false);
      setIsPaused(false);
    };

    utterance.onerror = () => {
      setIsPlaying(false);
      setIsPaused(false);
    };

    window.speechSynthesis.speak(utterance);
    setIsPlaying(true);
    setIsPaused(false);
  };

  const handlePause = () => {
    if ('speechSynthesis' in window && isPlaying) {
      window.speechSynthesis.pause();
      setIsPlaying(false);
      setIsPaused(true);
    }
  };

  const handleStop = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      setIsPaused(false);
    }
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1.5">
        {!isPlaying && !isPaused ? (
          <button
            type="button"
            onClick={handlePlay}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold transition-colors cursor-pointer shadow-xs min-h-[38px]"
            aria-label="Listen to today's advice audio"
          >
            <Volume2 className="w-4 h-4 text-white" />
            <span>{t.listenAudio}</span>
          </button>
        ) : (
          <div className="inline-flex items-center gap-1 bg-emerald-100 border border-emerald-300 p-1 rounded-lg">
            {isPlaying ? (
              <button
                type="button"
                onClick={handlePause}
                className="px-2.5 py-1 rounded bg-emerald-700 text-white text-xs font-bold flex items-center gap-1 cursor-pointer min-h-[32px]"
                aria-label="Pause audio"
              >
                <Pause className="w-3.5 h-3.5" />
                <span>{t.pausedAudio}</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={handlePlay}
                className="px-2.5 py-1 rounded bg-emerald-700 text-white text-xs font-bold flex items-center gap-1 cursor-pointer min-h-[32px]"
                aria-label="Resume audio"
              >
                <Play className="w-3.5 h-3.5" />
                <span>{t.listenAudio}</span>
              </button>
            )}

            <button
              type="button"
              onClick={handleStop}
              className="p-1 rounded hover:bg-emerald-200 text-emerald-900 cursor-pointer min-h-[32px] min-w-[32px] flex items-center justify-center"
              aria-label="Stop audio"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
            </button>
          </div>
        )}
      </div>

      {/* Regional TTS Voice Unavailable Notice */}
      {voiceNotice && (
        <p className="text-[11px] font-semibold text-amber-800 flex items-center gap-1 bg-amber-50 p-2 rounded border border-amber-200">
          <AlertCircle className="w-3.5 h-3.5 text-amber-700 shrink-0" />
          <span>{voiceNotice}</span>
        </p>
      )}
    </div>
  );
};
