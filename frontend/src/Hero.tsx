import { useDarkTheme, useMediaQuery } from './hooks';

export default function Hero({ className = '' }: { className?: string }) {
  // const isMobile = window.innerWidth <= 768;
  const { isMobile } = useMediaQuery();
  const [isDarkTheme] = useDarkTheme();
  return null;
}
