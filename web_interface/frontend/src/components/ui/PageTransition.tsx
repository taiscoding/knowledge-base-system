import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { Box } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { RESPONSIVE } from '../../utils/responsive';

interface PageTransitionProps {
  children: ReactNode;
  transitionType?: 'fade' | 'slide' | 'scale' | 'none';
}

/**
 * Page Transition Component
 * Wraps page content with animated transitions between routes
 * 
 * @param children - The page content to display
 * @param transitionType - The type of transition to use (fade, slide, scale, none)
 */
const PageTransition: React.FC<PageTransitionProps> = ({ 
  children, 
  transitionType = 'fade' 
}) => {
  const location = useLocation();
  
  // No animation if 'none' is specified
  if (transitionType === 'none') {
    return <>{children}</>;
  }
  
  // Animation variants based on transition type
  const variants = {
    fade: {
      initial: { opacity: 0 },
      animate: { opacity: 1 },
      exit: { opacity: 0 },
    },
    slide: {
      initial: { x: 20, opacity: 0 },
      animate: { x: 0, opacity: 1 },
      exit: { x: -20, opacity: 0 },
    },
    scale: {
      initial: { scale: 0.96, opacity: 0 },
      animate: { scale: 1, opacity: 1 },
      exit: { scale: 0.95, opacity: 0 },
    },
  };
  
  const selectedVariant = variants[transitionType];
  
  return (
    <motion.div
      key={location.pathname}
      initial="initial"
      animate="animate"
      exit="exit"
      variants={selectedVariant}
      transition={{
        duration: 0.25,
        ease: RESPONSIVE.animation.easing.smooth,
      }}
      style={{ width: '100%' }}
    >
      <Box width="100%">{children}</Box>
    </motion.div>
  );
};

export default PageTransition; 