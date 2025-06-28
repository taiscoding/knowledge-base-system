import { useMediaQuery, useTheme } from '@mui/material';

/**
 * Hook to determine if the current screen size is for a mobile device
 * @returns boolean true if the screen is mobile-sized
 */
export const useMobileSize = (): boolean => {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.down('sm'));
};

/**
 * Hook to determine if the current screen size is for a tablet device
 * @returns boolean true if the screen is tablet-sized
 */
export const useTabletSize = (): boolean => {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.between('sm', 'md'));
};

/**
 * Hook to determine if the current screen size is for a desktop device
 * @returns boolean true if the screen is desktop-sized
 */
export const useDesktopSize = (): boolean => {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.up('md'));
};

/**
 * Generic hook to get device-appropriate props for components
 * @param mobileProps - Props to use for mobile devices
 * @param tabletProps - Props to use for tablet devices
 * @param desktopProps - Props to use for desktop devices
 * @returns The appropriate props for the current screen size
 */
export function useResponsiveProps<T>(mobileProps: T, tabletProps: T, desktopProps: T): T {
  const isMobile = useMobileSize();
  const isTablet = useTabletSize();
  
  if (isMobile) {
    return mobileProps;
  } else if (isTablet) {
    return tabletProps;
  } else {
    return desktopProps;
  }
}

/**
 * Constants for responsive design values
 */
export const RESPONSIVE = {
  spacing: {
    xs: 1,    // 8px
    sm: 2,    // 16px
    md: 3,    // 24px
    lg: 4,    // 32px
    xl: 5     // 40px
  },
  fontSize: {
    small: {
      h1: '1.8rem',
      h2: '1.5rem',
      h3: '1.3rem',
      h4: '1.2rem',
      h5: '1.1rem',
      h6: '1rem',
      body: '0.9rem',
    },
    medium: {
      h1: '2.4rem',
      h2: '1.8rem',
      h3: '1.5rem',
      h4: '1.3rem',
      h5: '1.2rem',
      h6: '1.1rem',
      body: '1rem',
    },
    large: {
      h1: '2.8rem',
      h2: '2.2rem',
      h3: '1.8rem',
      h4: '1.5rem',
      h5: '1.3rem',
      h6: '1.2rem',
      body: '1.1rem',
    }
  },
  animation: {
    speed: {
      fast: '0.2s',
      normal: '0.3s',
      slow: '0.5s'
    },
    easing: {
      smooth: [0.4, 0, 0.2, 1],
      accelerate: [0.4, 0, 1, 1],
      decelerate: [0, 0, 0.2, 1]
    }
  }
}; 