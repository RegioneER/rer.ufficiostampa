import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

const rootElement = document.getElementById('comunicati-search');
rootElement.classList.add('row');

ReactDOM.render(<App />, rootElement);
