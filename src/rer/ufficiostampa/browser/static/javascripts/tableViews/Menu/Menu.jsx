import React, { useContext } from 'react';
import { TranslationsContext } from '../../TranslationsContext';
import { ApiContext } from '../../ApiContext';
import apiFetch from '../../utils/apiFetch';
import { saveAs } from 'file-saver';
import PropTypes from 'prop-types';

import './Menu.less';

const Menu = ({ editUser }) => {
  const getTranslationFor = useContext(TranslationsContext);
  const {
    portalUrl,
    fetchApi,
    handleApiResponse,
    apiErrors,
    setApiErrors,
    endpoint,
  } = useContext(ApiContext);

  const deleteAllUsers = () => {
    if (
      window.confirm(
        getTranslationFor(
          'Are you sure you want to delete all data?',
          'Are you sure you want to delete all data?',
        ),
      )
    ) {
      let fetches = [
        apiFetch({
          url: portalUrl + '/@' + endpoint + '-clear',
          method: 'GET',
        }),
      ];

      Promise.all(fetches).then(data => {
        handleApiResponse(data[0]);
        fetchApi();
      });
    }
  };

  const downloadCSV = () => {
    apiFetch({
      url: portalUrl + '/@' + endpoint + '-csv',
      method: 'GET',
    })
      .then(res => {
        if (!res) {
          setApiErrors({
            status: 404,
            statusText: getTranslationFor(
              'Url not found. Unable to download this file.',
              'Url not found. Unable to download this file.',
            ),
          });
          return;
        }
        if (res.status !== 200) {
          switch (res.status) {
            case 401:
            case 403:
              setApiErrors({
                status: res.status,
                statusText: getTranslationFor(
                  'You do not have permission to download this file.',
                  'You do not have permission to download this file.',
                ),
              });
              return;
            default:
              setApiErrors({
                status: res.status,
                statusText: getTranslationFor(
                  'An error occurred downloading file.',
                  'An error occurred downloading file.',
                ),
              });
              return;
          }
        }
        if (!res.data || res.data.length === 0) {
          setApiErrors({
            status: res.status,
            statusText: getTranslationFor(
              'An error occurred downloading file.',
              'An error occurred downloading file.',
            ),
          });
          return;
        }
        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        const disposition = res.headers['content-disposition'];
        if (disposition && disposition.indexOf('attachment') !== -1) {
          const matches = filenameRegex.exec(disposition);
          const filename = matches[1].replace(/['"]/g, '');
          const blob = new Blob([res.data], {
            type: res.headers['content-type'],
          });
          saveAs(blob, filename);
        }
      })
      .catch(err => {
        console.error(err);
        setApiErrors({
          status: 500,
          statusText: err.message,
        });
      });
  };

  return (
    <>
      <div className="ufficiostampa-menu-wrapper">
        {endpoint === 'subscriptions' ? (
          <button
            onClick={() => editUser()}
            className="plone-btn plone-btn-primary"
          >
            {getTranslationFor('Add Subscriber', 'Add subscriber')}
          </button>
        ) : (
          ''
        )}
        <button
          onClick={() => deleteAllUsers()}
          className="plone-btn plone-btn-danger"
        >
          {getTranslationFor('Delete all data', 'Delete all data')}
        </button>
        <button
          onClick={() => downloadCSV()}
          className="plone-btn plone-btn-primary"
        >
          {getTranslationFor('Export in CSV', 'Export in CSV')}
        </button>
        <button className="plone-btn plone-btn-primary">
          {getTranslationFor('Import from CSV', 'Import from CSV')}
        </button>
      </div>

      {apiErrors && (
        <div className="errors">
          <dl className="portalMessage error" role="alert">
            <dt>Error. Status code: {apiErrors.status}</dt>
            <dd>{apiErrors.statusText}</dd>
          </dl>
        </div>
      )}
    </>
  );
};

Menu.propTypes = {
  editUser: PropTypes.func,
};

export default Menu;
