import type { Metadata } from "next";
import { Space_Grotesk, Instrument_Sans } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-space-grotesk',
  display: 'swap',
});

const instrumentSans = Instrument_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-instrument-sans',
  display: 'swap',
});

export const metadata: Metadata = {
  title: "reddit this. — Find your corner",
  description: "Type a worry. We surface the best threads—smart, not keyword-dumb.",
  keywords: ["reddit", "search", "community", "conversations", "discussions", "connect"],
  themeColor: '#0A0A0A',
  openGraph: {
    title: "reddit this. — Find your corner",
    description: "Type a worry. We surface the best threads—smart, not keyword-dumb.",
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${spaceGrotesk.variable} ${instrumentSans.variable} antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
