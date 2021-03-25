import React, { useState, useEffect } from 'react';
import { TranslationsConsumer } from '../TranslationsContext';
import apiFetch from '../utils/apiFetch';

const UsersList = ({ portalUrl }) => {
  //ON FIRST LOAD
  useEffect(() => {}, []);

  return (
    <></>
    // <TranslationsConsumer>
    //   {getTranslationFor => {
    //     {
    //       searchResults.items?.length > 0 && (
    //         <>Ci sono {searchResults.items_total} risultati da mostrare</>
    //       );
    //     }
    //   }}
    // </TranslationsConsumer>
  );
};
export default UsersList;
