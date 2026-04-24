import { createGlobalStyle } from 'styled-components';

export const GlobalStyles = createGlobalStyle`
  :root {
    --primary: #2d6a4f;
    --secondary: #40916c;
    --accent: #52b788;
    --background: #f8f9fa;
    --text: #1b4332;
    --white: #ffffff;
    --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    --glass: rgba(255, 255, 255, 0.8);
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background: linear-gradient(135deg, #d8f3dc 0%, #b7e4c7 100%);
    color: var(--text);
    min-height: 100vh;
  }

  h1, h2, h3 {
    font-weight: 700;
  }

  button {
    cursor: pointer;
    border: none;
    outline: none;
    transition: all 0.3s ease;
  }
`;
