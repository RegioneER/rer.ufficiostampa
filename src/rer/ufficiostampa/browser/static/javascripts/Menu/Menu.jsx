import React, { useState, useEffect, useContext } from 'react';
import { TranslationsContext } from '../TranslationsContext';

const Menu = ({ portalUrl, editUser }) => {
  const getTranslationFor = useContext(TranslationsContext);

  return (
    <>
      <div className="ufficiostampa-menu-wrapper">
        <button
          onClick={() => editUser()}
          className="plone-btn plone-btn-primary"
        >
          {getTranslationFor('Add Subscriber', 'Add subscriber')}
        </button>
      </div>
    </>
  );
};
export default Menu;
