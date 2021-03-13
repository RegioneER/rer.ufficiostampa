import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TranslationsWrapper from './TranslationsContext';

import './App.less';

const App = () => {

  const portalUrl = document.body
    ? document.body.getAttribute('data-portal-url') || ''
    : '';
  useEffect(() => {
    axios({
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        Accept: 'application/json',
      },
      url: `${portalUrl}/@search_parameters`,
    }).then(({ status, statusText, data }) => {
      if (status !== 200) {
        console.error(statusText);
      } else {
        setFormParameters(data);
        setFetching(false);
        initializeQueryParameters(data);
      }
    });
  }, []);

  const initializeQueryParameters = parameters => {
    const queryString = new URLSearchParams(window.location.search);
    const newParameters = parameters.reduce((accumulator, parameter) => {
      switch (parameter.type) {
        case 'text':
          accumulator[parameter.id] = queryString.get(parameter.id) || '';
          break;
        default:
          if (!queryString.get(parameter.id)) {
            //  empty
            accumulator[parameter.id] = [];
          } else {
            accumulator[parameter.id] = queryString.getAll(parameter.id);
          }
          break;
      }

      return accumulator;
    }, {});
    setQueryParameters({ ...queryParameters, ...newParameters });
  };

  const updateQueryParameters = parameter => {
    const newQueryParameters = { ...queryParameters, ...parameter };
    setQueryParameters(newQueryParameters);
    history.pushState(
      { id: 'search_bandi_form' },
      'Search Bandi',
      `${portalUrl}/search_bandi_form?${queryString.stringify(
        newQueryParameters,
      )}`,
    );
  };

  const resetQueryParameters = () => {
    const newQueryParameters = { b_start: 0, b_size: 20 };
    setQueryParameters(newQueryParameters);
    history.pushState(
      { id: 'search_bandi_form' },
      'Search Bandi',
      `${portalUrl}/search_bandi_form`,
    );
  };

  return (
    <TranslationsWrapper>
      <FiltersWrapper
        updateQueryParameters={updateQueryParameters}
        resetQueryParameters={resetQueryParameters}
        formParameters={formParameters}
        queryParameters={queryParameters}
        isFetching={isFetching}
      ></FiltersWrapper>
      <ResultsWrapper
        queryParameters={queryParameters}
        updateQueryParameters={updateQueryParameters}
      ></ResultsWrapper>
    </TranslationsWrapper>
  );
};
export default App;
