import Link from 'next/link';
import './globals.css'; // Ensure consistent styling

export const metadata = {};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <nav
          className='bg-background-800 border-b border-background-400 text-white flex gap-4 p-3 '
        >
          <Link href="/" style={{ textDecoration: 'none' }}>
            Home
          </Link>
          <Link href="/docs" style={{ textDecoration: 'none' }}>
            Documentation
          </Link>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
