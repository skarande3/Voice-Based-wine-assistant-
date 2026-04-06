import { motion } from "motion/react";

export default function VoiceWaveform() {
  const bars = 20;

  return (
    <div className="flex items-center gap-1 h-12">
      {Array.from({ length: bars }).map((_, i) => (
        <motion.div
          key={i}
          animate={{
            height: ["20%", `${30 + Math.random() * 70}%`, "20%"],
          }}
          transition={{
            duration: 0.5 + Math.random() * 0.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.05,
          }}
          className="w-1 bg-gradient-to-t from-red-500 to-red-300 rounded-full"
        />
      ))}
    </div>
  );
}
