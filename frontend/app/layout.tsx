import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NDB Code Visualizer',
  description: 'See how tight the ndb code is'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="Nutanix-Era-40.svg" sizes="any" />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
