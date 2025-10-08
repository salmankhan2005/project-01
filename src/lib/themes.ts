interface ThemeColors {
  primary: string;
  primaryHover: string;
  secondary: string;
  accent: string;
  accentHover: string;
  background: string;
  cardBackground: string;
  muted: string;
  mutedHover: string;
}

export const themeColors: Record<string, ThemeColors> = {
  light: {
    primary: 'bg-purple-500',
    primaryHover: 'hover:bg-purple-600',
    secondary: 'bg-purple-400',
    accent: 'text-purple-500',
    accentHover: 'hover:text-purple-600',
    background: 'bg-white',
    cardBackground: 'bg-white',
    muted: 'bg-gray-100',
    mutedHover: 'hover:bg-gray-200',
  },
  dark: {
    primary: 'bg-purple-500',
    primaryHover: 'hover:bg-purple-600',
    secondary: 'bg-purple-400',
    accent: 'text-purple-400',
    accentHover: 'hover:text-purple-300',
    background: 'bg-background/95',
    cardBackground: 'bg-background/60',
    muted: 'bg-muted/40',
    mutedHover: 'hover:bg-purple-500/20',
  },
  'comic-dark': {
    primary: 'bg-pink-500',
    primaryHover: 'hover:bg-pink-600',
    secondary: 'bg-pink-400',
    accent: 'text-pink-400',
    accentHover: 'hover:text-pink-300',
    background: 'bg-background/95',
    cardBackground: 'bg-background/60',
    muted: 'bg-muted/40',
    mutedHover: 'hover:bg-pink-500/20',
  },
  'clean-minimalist-dark': {
    primary: 'bg-blue-500',
    primaryHover: 'hover:bg-blue-600',
    secondary: 'bg-blue-400',
    accent: 'text-blue-400',
    accentHover: 'hover:text-blue-300',
    background: 'bg-background/95',
    cardBackground: 'bg-background/60',
    muted: 'bg-muted/40',
    mutedHover: 'hover:bg-blue-500/20',
  },
  // Add more theme variants as needed
};