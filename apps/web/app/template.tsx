"use client";

import { motion } from "framer-motion";
import { pageVariants } from "@/lib/motion";

// App Router page transition — enter animation on every navigation.
export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div variants={pageVariants} initial="initial" animate="animate">
      {children}
    </motion.div>
  );
}
