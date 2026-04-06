import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Mic, Settings, Volume2 } from "lucide-react";
import onkiLogo from "../../assets/a51083523ca7ee8adb33531762b1cf7796059b7a.png";
import VoiceWaveform from "../components/VoiceWaveform";
import MascotCharacter from "../components/MascotCharacter";
import TextInputFallback from "../components/TextInputFallback";
import { askWineQuestion, getHealth, type ApiWineResult } from "../utils/api";

type VoiceState = "idle" | "listening" | "processing" | "responding";

export default function VoiceInterface() {
  const [state, setState] = useState<VoiceState>("idle");
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState("");
  const [results, setResults] = useState<ApiWineResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasVoiceSupport, setHasVoiceSupport] = useState(false);
  
  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const latestStateRef = useRef<VoiceState>("idle");
  const latestTranscriptRef = useRef("");

  useEffect(() => {
    latestStateRef.current = state;
  }, [state]);

  useEffect(() => {
    latestTranscriptRef.current = transcript;
  }, [transcript]);

  useEffect(() => {
    setIsLoading(true);
    getHealth()
      .then(() => {
        setIsLoading(false);
      })
      .catch(() => {
        setError("The backend is unavailable. Start the FastAPI server and try again.");
        setIsLoading(false);
      });
    synthRef.current = window.speechSynthesis;
    
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setHasVoiceSupport(true);
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const current = event.resultIndex;
        const transcriptText = event.results[current][0].transcript;
        setTranscript(transcriptText);
      };

      recognitionRef.current.onend = () => {
        if (latestStateRef.current === "listening") {
          void handleProcessing(latestTranscriptRef.current);
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setError("Sorry, I couldn't hear that. Please try again.");
        setState("idle");
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  const startListening = () => {
    if (!recognitionRef.current) {
      setError("Voice recognition is not supported in your browser.");
      return;
    }

    setTranscript("");
    setResponse("");
    setError("");
    setState("listening");
    recognitionRef.current.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const handleProcessing = async (questionText: string) => {
    if (!questionText.trim()) {
      setError("I didn't catch a question. Please try again.");
      setState("idle");
      return;
    }

    setState("processing");

    try {
      const apiResponse = await askWineQuestion(questionText);
      setResponse(apiResponse.answer_text);
      setResults(apiResponse.results);
      setState("responding");

      if (synthRef.current && apiResponse.answer_text) {
        synthRef.current.cancel();
        const utterance = new SpeechSynthesisUtterance(apiResponse.answer_text);
        utterance.rate = 0.9;
        utterance.onend = () => {
          setTimeout(() => {
            setState("idle");
          }, 1000);
        };
        synthRef.current.speak(utterance);
      }
    } catch (requestError) {
      console.error(requestError);
      setError("I couldn't reach the backend. Please make sure the API server is running.");
      setResults([]);
      setState("idle");
    }
  };

  const handleMicClick = () => {
    if (state === "idle") {
      startListening();
    } else if (state === "listening") {
      stopListening();
    }
  };

  const handleTextSubmit = (text: string) => {
    setTranscript(text);
    setResponse("");
    setResults([]);
    setError("");
    void handleProcessing(text);
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-br from-[#5B0F1A] via-[#2a0a0f] to-black">
      {/* Ambient background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-20 w-96 h-96 bg-[#5B0F1A] rounded-full blur-[120px]" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-[#8B1E2F] rounded-full blur-[120px]" />
      </div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between p-6">
        <img src={onkiLogo} alt="Onki" className="w-12 h-12 object-contain bg-white rounded-full p-2" />
        <button className="p-2 rounded-full bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-colors">
          <Settings className="w-5 h-5 text-white" />
        </button>
      </header>

      {/* Main Content */}
      <div className="relative min-h-screen w-full flex flex-col items-center justify-start px-6 pt-24 pb-[18rem] sm:pt-20 sm:pb-[17rem]">
        {/* Mascot */}
        <MascotCharacter state={state} />

        {/* Transcript Panel */}
        <AnimatePresence mode="wait">
          {transcript && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8 max-w-2xl w-full"
            >
              <div className="bg-white/10 backdrop-blur-md rounded-3xl px-6 py-4 border border-white/20 shadow-xl">
                <p className="text-white/60 text-sm mb-2">You asked:</p>
                <p className="text-white text-lg">{transcript}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Processing Indicator */}
        <AnimatePresence mode="wait">
          {state === "processing" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="mt-8 flex gap-2"
            >
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  animate={{
                    scale: [1, 1.4, 1],
                    opacity: [0.5, 1, 0.5],
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: i * 0.2,
                  }}
                  className="w-3 h-3 rounded-full bg-white/60"
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Response Panel */} 
        <AnimatePresence mode="wait">
          {response && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8 max-w-2xl w-full"
            >
              <div className="bg-white/10 backdrop-blur-md rounded-3xl px-6 py-5 border border-white/20 shadow-xl">
                <div className="flex items-center gap-2 mb-3">
                  <Volume2 className="w-5 h-5 text-white/60" />
                  <p className="text-white/60 text-sm">Wineard says:</p>
                </div>
                <p className="text-white text-lg leading-relaxed">{response}</p>
                {results.length > 0 && (
                  <div className="mt-5 space-y-3">
                    {results.slice(0, 3).map((wine) => (
                      <div
                        key={`${wine.id ?? wine.name}`}
                        className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3"
                      >
                        <p className="text-white font-medium">{wine.name}</p>
                        <p className="text-white/70 text-sm">
                          {[wine.region, wine.country].filter(Boolean).join(", ")}
                          {wine.price != null ? ` • $${wine.price.toFixed(2)}` : ""}
                          {wine.rating != null ? ` • ${wine.rating}/100` : ""}
                        </p>
                        {wine.match_reason && (
                          <p className="mt-2 text-white/55 text-sm">{wine.match_reason}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Message */}
        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8 max-w-2xl w-full"
            >
              <div className="bg-red-500/20 backdrop-blur-md rounded-3xl px-6 py-4 border border-red-500/30">
                <p className="text-white text-center">{error}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading Indicator */}
        <AnimatePresence mode="wait">
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8 max-w-2xl w-full"
            >
              <div className="bg-white/10 backdrop-blur-md rounded-3xl px-6 py-4 border border-white/20 shadow-xl">
                <p className="text-white/60 text-sm mb-2">Loading...</p>
                <p className="text-white text-lg">Please wait while we load the wine data.</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-20 flex justify-center px-4 pb-6 sm:px-6">
        <div className="pointer-events-auto flex w-full max-w-3xl flex-col items-center gap-3 rounded-[2rem] bg-black/10 px-3 py-4 backdrop-blur-md sm:gap-4 sm:px-4">
          {state === "idle" && !response && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="w-full"
            >
              <div className="flex flex-wrap justify-center gap-2">
                {[
                  "Best wines under $50",
                  "From Burgundy",
                  "Most expensive bottle",
                ].map((prompt, i) => (
                  <motion.button
                    key={i}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                      setTranscript(prompt);
                      setResponse("");
                      setResults([]);
                      setError("");
                      void handleProcessing(prompt);
                    }}
                    className="px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white/80 text-sm hover:bg-white/20 transition-all"
                  >
                    {prompt}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {!hasVoiceSupport && (
            <div className="text-center text-sm text-white/60">
              Voice input is not available in this browser, so you can type your question below.
            </div>
          )}

          <div className="w-full max-w-2xl">
            <TextInputFallback onSubmit={handleTextSubmit} disabled={state === "processing" || isLoading} />
          </div>

          <div className="flex flex-col items-center gap-3 pt-1">
            {state === "listening" && <VoiceWaveform />}

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleMicClick}
              disabled={state === "processing" || state === "responding"}
              className={`
                relative w-20 h-20 rounded-full flex items-center justify-center
                backdrop-blur-xl border-2 shadow-2xl transition-all duration-300
                ${
                  state === "idle"
                    ? "bg-white/20 border-white/30 hover:bg-white/30"
                    : state === "listening"
                    ? "bg-red-500/30 border-red-400/50 shadow-red-500/50"
                    : "bg-white/10 border-white/20 opacity-50 cursor-not-allowed"
                }
              `}
            >
              <Mic className={`w-8 h-8 ${state === "listening" ? "text-red-400" : "text-white"}`} />

              {state === "idle" && (
                <motion.div
                  animate={{
                    scale: [1, 1.3, 1],
                    opacity: [0.5, 0, 0.5],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                  }}
                  className="absolute inset-0 rounded-full bg-white/30"
                />
              )}

              {state === "listening" && (
                <motion.div
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.4, 0, 0.4],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                  }}
                  className="absolute inset-0 rounded-full bg-red-500/50"
                />
              )}
            </motion.button>

            <motion.p
              animate={{ opacity: [0.6, 1, 0.6] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="text-white/60 text-sm"
            >
              {state === "idle" && "Tap to ask about wine"}
              {state === "listening" && "Listening..."}
              {state === "processing" && "Thinking..."}
              {state === "responding" && "Speaking..."}
            </motion.p>
          </div>
        </div>
      </div>
    </div>
  );
}
