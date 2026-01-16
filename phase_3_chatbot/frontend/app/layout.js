import './globals.css';
import ChatKitWidget from '../components/ChatKitWidget';

export const metadata = {
  title: 'Todo AI Chatbot',
  description: 'AI-powered Todo Management Assistant',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <ChatKitWidget />
      </body>
    </html>
  );
}