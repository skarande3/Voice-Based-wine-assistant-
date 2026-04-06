import { useNavigate } from "react-router";
import { motion } from "motion/react";
import onkiLogo from "../../assets/a51083523ca7ee8adb33531762b1cf7796059b7a.png";

export default function WelcomeScreen() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-br from-[#5B0F1A] via-[#2a0a0f] to-black">
      {/* Ambient background blur */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-20 w-96 h-96 bg-[#5B0F1A] rounded-full blur-[120px]" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-[#8B1E2F] rounded-full blur-[120px]" />
      </div>

      {/* Content */}
      <div className="relative min-h-screen w-full flex flex-col items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex flex-col items-center gap-8"
        >
          {/* Logo */}
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="w-32 h-32 rounded-full bg-white p-4 shadow-2xl shadow-[#5B0F1A]/50"
          >
            <img src={onkiLogo} alt="Onki" className="w-full h-full object-contain" />
          </motion.div>

          {/* Heading */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-center space-y-3"
          >
            <h1 className="text-5xl md:text-6xl font-bold text-white tracking-tight">
              Discover wine.
              <br />
              Just ask.
            </h1>
            <p className="text-lg md:text-xl text-white/70">
              Your voice-powered wine assistant
            </p>
          </motion.div>

          {/* CTA Button */}
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate("/intro")}
            className="mt-8 px-10 py-4 rounded-full bg-white text-[#5B0F1A] font-semibold text-lg shadow-lg shadow-white/20 hover:shadow-xl hover:shadow-white/30 transition-all duration-300"
          >
            Start Exploring
          </motion.button>

          {/* Subtle pulse animation */}
          <motion.div
            animate={{
              opacity: [0.3, 0.6, 0.3],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="absolute inset-0 pointer-events-none"
          >
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
