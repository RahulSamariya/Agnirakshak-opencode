import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Heatwave Early Warning Platform',
  description: 'Extreme Heatwave Early Warning and Human Thermal Stress Index',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
