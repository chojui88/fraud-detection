import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// React 앱의 시작점 — public/index.html의 <div id="root">에 앱을 렌더링한다
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
