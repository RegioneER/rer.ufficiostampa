import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { object, func } from 'prop-types';
import { TranslationsContext } from '../../../TranslationsContext';
import ResultsList from '../ResultsList';

const Spinner = require('react-spinkit');

import './index.less';

const ResultsWrapper = ({ queryParameters, updateQueryParameters }) => {
  const [isFetching, setFetching] = useState(false);
  const [results, setResults] = useState({});
  const getTranslationFor = useContext(TranslationsContext);

  const portalUrl = document.body
    ? document.body.getAttribute('data-portal-url') || ''
    : '';

  const parseParams = params => {
    const keys = Object.keys(params);
    let options = '';

    keys.forEach(key => {
      if (params[key]) {
        const isParamTypeObject = typeof params[key] === 'object';
        const isParamTypeArray = isParamTypeObject && params[key].length >= 0;

        if (!isParamTypeObject) {
          options += `${key}=${params[key]}&`;
        }

        if (isParamTypeObject && isParamTypeArray) {
          params[key].forEach(element => {
            options += `${key}=${element}&`;
          });
        }
      }
    });

    return options ? options.slice(0, -1) : options;
  };
  const doQuery = () => {
    let params = Object.keys(queryParameters).reduce(
      (acc, key) => {
        const value = queryParameters[key];
        if (value !== '' || value !== null) {
          if (key === 'created') {
            if (value.from) {
              if (value.to) {
                acc['created.query'] = [
                  value.from.format('YYYY-MM-DD 00:00:00'),
                  value.to.format('YYYY-MM-DD 23:59:59'),
                ];
                acc['created.range'] = 'min:max';
              } else {
                acc['created.query'] = value.from.format('YYYY-MM-DD 00:00:00');
                acc['created.range'] = 'min';
              }
            }
          } else {
            acc[key] = value;
          }
        }
        return acc;
      },
      {
        sort_on: 'effective',
        sort_order: 'reverse',
        metadata_fields: [
          'arguments',
          'legislature',
          'UID',
          'effective',
          'created',
        ],
      },
    );
    if (!params.portal_type || params.portal_type.length === 0) {
      params.portal_type = ['ComunicatoStampa', 'InvitoStampa'];
    }
    setFetching(true);
    axios({
      method: 'GET',
      headers: {
        'content-type': 'application/json',
        Accept: 'application/json',
      },
      url: `${portalUrl}/@search-comunicati`,
      params,
      paramsSerializer: params => parseParams(params),
    }).then(({ status, statusText, data }) => {
      if (status !== 200) {
        console.error(statusText);
      } else {
        setResults(data);
        setFetching(false);
      }
    });
  };

  useEffect(() => {
    doQuery();
  }, [JSON.stringify(queryParameters)]);

  const updatedPagination = parameter => {
    updateQueryParameters(parameter);
  };

  const resultsContent = isFetching ? (
    <Spinner name="three-bounce" fadeIn="none" className="spinner" />
  ) : (
    <ResultsList
      results={results}
      updatedPagination={updatedPagination}
      queryParameters={queryParameters}
    />
  );
  return (
    <div
      className="search-results col-md-8 col-sm-12"
      role="region"
      aria-live="polite"
      id="search-results-region"
      aria-relevant="additions removals"
    >
      {resultsContent}
      <a href="#comunicati-search-filters" className="sr-only">
        {getTranslationFor('go_to_search_filters', 'Go to filters')}
      </a>
    </div>
  );
};
ResultsWrapper.propTypes = {
  queryParameters: object,
  updateQueryParameters: func,
};

export default ResultsWrapper;
