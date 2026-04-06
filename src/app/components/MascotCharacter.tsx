import { motion } from "motion/react";
import mascotListening from "../../assets/f85097a350e3eb533eb4abd31b1ca4e12ded480a.png";
import mascotIdle from "../../assets/df03b0bdf2ad2b0947ce3a45bd56925e7c18b5a5.png";

type VoiceState = "idle" | "listening" | "processing" | "responding";

interface MascotCharacterProps {
  state: VoiceState;
}

export default function MascotCharacter({ state }: MascotCharacterProps) {
  // Different animations for different states
  const animations = {
    idle: {
      y: [0, -8, 0],
      rotate: [0, 0, 0],
      scale: 1,
    },
    listening: {
      y: [-5, -5, -5],
      rotate: [-3, 3, -3],
      scale: 1.05,
    },
    processing: {
      y: [0, 0, 0],
      rotate: [0, 0, 0],
      scale: [1, 1.02, 1],
    },
    responding: {
      y: [0, -5, 0],
      rotate: [0, 0, 0],
      scale: 1,
    },
  };

  const transition = {
    idle: {
      duration: 3,
      repeat: Infinity,
      ease: "easeInOut",
    },
    listening: {
      duration: 0.8,
      repeat: Infinity,
      ease: "easeInOut",
    },
    processing: {
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut",
    },
    responding: {
      duration: 1.2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  };

  // Choose mascot image based on state
  const mascotImage = state === "listening" ? mascotListening : mascotIdle;

  return (
    <div className="relative">
      {/* Glow effect */}
      <motion.div
        animate={{
          opacity: state === "processing" ? [0.3, 0.6, 0.3] : [0.2, 0.4, 0.2],
          scale: state === "listening" ? [1, 1.3, 1] : [1, 1.2, 1],
        }}
        transition={{
          duration: state === "processing" ? 1.5 : 2.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className={`absolute inset-0 -m-8 rounded-full blur-3xl ${
          state === "listening"
            ? "bg-red-500/40"
            : state === "processing"
            ? "bg-yellow-500/40"
            : state === "responding"
            ? "bg-green-500/40"
            : "bg-white/20"
        }`}
      />

      {/* Mascot */}
      <motion.div
        animate={animations[state]}
        transition={transition[state]}
        className="relative w-64 h-64 md:w-72 md:h-72"
      >
        <img
          src={mascotImage}
          alt="Wineard"
          className="w-full h-full object-contain"
        />
      </motion.div>

      {/* State indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap"
      >
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm">
          <motion.div
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
            }}
            className={`w-2 h-2 rounded-full ${
              state === "listening"
                ? "bg-red-400"
                : state === "processing"
                ? "bg-yellow-400"
                : state === "responding"
                ? "bg-green-400"
                : "bg-white/60"
            }`}
          />
          <p className="text-white/80 text-sm font-medium">
            {state === "idle" && "Ready"}
            {state === "listening" && "Listening"}
            {state === "processing" && "Thinking"}
            {state === "responding" && "Speaking"}
          </p>
        </div>
      </motion.div>
    </div>
  );
}
