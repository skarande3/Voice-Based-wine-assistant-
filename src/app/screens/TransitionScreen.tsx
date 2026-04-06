import { useEffect } from "react";
import { useNavigate } from "react-router";
import { motion } from "motion/react";
import onkiLogo from "../../assets/a51083523ca7ee8adb33531762b1cf7796059b7a.png";

export default function TransitionScreen() {
  const navigate = useNavigate();

  useEffect(() => {
    // Auto-navigate to main interface after animation
    const timer = setTimeout(() => {
      navigate("/assistant");
    }, 3500);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-br from-[#5B0F1A] via-[#2a0a0f] to-black">
      {/* Ambient background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-20 w-96 h-96 bg-[#5B0F1A] rounded-full blur-[120px]" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-[#8B1E2F] rounded-full blur-[120px]" />
      </div>

      {/* Content */}
      <div className="relative min-h-screen w-full flex flex-col items-center justify-center px-6">
        {/* Mascot */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="mb-8"
        >
          <motion.div
            animate={{
              y: [0, -10, 0],
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="w-40 h-40 rounded-full bg-white p-6 shadow-2xl shadow-[#5B0F1A]/50"
          >
            <img src={onkiLogo} alt="Wineard" className="w-full h-full object-contain" />
          </motion.div>
        </motion.div>

        {/* Typing animation text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
          className="text-center"
        >
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.8 }}
            className="text-4xl md:text-5xl font-bold text-white"
          >
            Hi! I'm Wineard 🍷
          </motion.h2>
          
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2, duration: 0.8 }}
            className="mt-4 text-lg text-white/70"
          >
            Let's explore wines together
          </motion.p>
        </motion.div>

        {/* Loading indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.5, duration: 0.5 }}
          className="mt-12 flex gap-2"
        >
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{
                scale: [1, 1.3, 1],
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
      </div>
    </div>
  );
}
