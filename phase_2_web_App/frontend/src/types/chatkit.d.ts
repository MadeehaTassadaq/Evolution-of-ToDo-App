/**
 * Type declarations for OpenAI ChatKit Web Component
 * Adds support for <openai-chatkit> custom element
 */

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'openai-chatkit': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
        ref?: React.Ref<HTMLElement>;
        token?: string;
        serverUrl?: string;
        'server-url'?: string;
        apiURL?: string;
        'api-url'?: string;
        apiurl?: string;
        theme?: 'light' | 'dark';
        initialThread?: string | null;
        'initial-thread'?: string | null;
        class?: string;
        className?: string;
        style?: React.CSSProperties;
      };
    }
  }
}

export {};
