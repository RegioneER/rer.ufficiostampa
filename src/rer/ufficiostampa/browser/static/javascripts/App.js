import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TranslationsWrapper from './TranslationsContext';

import './App.less';

const App = () => {

  const portalUrl = document.body
    ? document.body.getAttribute('data-portal-url') || ''
    : '';
  return (
    <TranslationsWrapper>
      <div>CIAO</div>
    </TranslationsWrapper>
  );
};
export default App;
