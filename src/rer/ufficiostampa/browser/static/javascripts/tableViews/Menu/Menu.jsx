import React, { useContext, useState } from 'react';
import { TranslationsContext } from '../../TranslationsContext';
import { ApiContext } from '../../ApiContext';
import apiFetch from '../../utils/apiFetch';
import { downloadCSV } from '../CSV/ExportCSV';
import ImportCSV from '../CSV/ImportCSV';
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

  const [showImportCSV, setShowImportCSV] = useState(false);

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

  return (
    <>
      <div className="ufficiostampa-menu-wrapper">
        <div className="left-zone">
          {endpoint === 'subscriptions' && (
            <>
              <button
                onClick={() => editUser()}
                className="plone-btn plone-btn-primary"
              >
                {getTranslationFor('Add Subscriber', 'Add subscriber')}
              </button>
              <button
                className="plone-btn plone-btn-primary"
                onClick={() => setShowImportCSV(true)}
              >
                {getTranslationFor('Import from CSV', 'Import from CSV')}
              </button>
            </>
          )}
          <button
            onClick={() => downloadCSV(portalUrl, endpoint)}
            className="plone-btn plone-btn-primary"
          >
            {getTranslationFor('Export in CSV', 'Export in CSV')}
          </button>

          {endpoint === 'subscriptions' && (
            <a
              href={`${portalUrl}/ufficiostampa-settings`}
              className="plone-btn plone-btn-primary"
            >
              <span>{getTranslationFor('Settings', 'Settings')}</span>
            </a>
          )}
        </div>
        <div className="right-zone">
          <button
            onClick={() => deleteAllUsers()}
            className="plone-btn plone-btn-warning"
          >
            {getTranslationFor('Delete all data', 'Delete all data')}
          </button>
        </div>
      </div>

      {apiErrors && (
        <div className="errors">
          <dl className="portalMessage error" role="alert">
            <dt>Error. Status code: {apiErrors.status}</dt>
            <dd>{apiErrors.statusText}</dd>
          </dl>
        </div>
      )}

      <ImportCSV showModal={showImportCSV} setShowModal={setShowImportCSV} />
    </>
  );
};

Menu.propTypes = {
  editUser: PropTypes.func,
};

export default Menu;
