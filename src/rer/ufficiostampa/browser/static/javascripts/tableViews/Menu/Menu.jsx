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
    endpoint,
  } = useContext(ApiContext);

  const [showImportCSV, setShowImportCSV] = useState(false);

  const isSubscriptionPanel = endpoint === 'subscriptions';
  const deleteLabel = isSubscriptionPanel
    ? 'Delete all subscriptions'
    : 'Delete all data';

  const confirmDeleteLabel = isSubscriptionPanel
    ? 'Are you sure you want to delete all subscriptions?'
    : 'Are you sure you want to delete all data?';

  const deleteAllUsers = () => {
    if (
      window.confirm(getTranslationFor(confirmDeleteLabel, confirmDeleteLabel))
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
          {isSubscriptionPanel && (
            <>
              <button
                onClick={() => editUser()}
                className="plone-btn plone-btn-primary context"
              >
                {getTranslationFor('Add Subscriber', 'Add subscriber')}
              </button>
              <button
                className="plone-btn plone-btn-primary context"
                onClick={() => setShowImportCSV(true)}
              >
                {getTranslationFor('Import from CSV', 'Import from CSV')}
              </button>
            </>
          )}
          <button
            onClick={() => downloadCSV(portalUrl, endpoint)}
            className="plone-btn plone-btn-primary context"
          >
            {getTranslationFor('Export in CSV', 'Export in CSV')}
          </button>

          {isSubscriptionPanel && (
            <a
              href={`${portalUrl}/ufficiostampa-settings`}
              className="plone-btn plone-btn-primary context"
            >
              <span>{getTranslationFor('Settings', 'Settings')}</span>
            </a>
          )}
        </div>
        <div className="right-zone">
          <button
            onClick={() => deleteAllUsers()}
            className="plone-btn plone-btn-danger"
          >
            {getTranslationFor(deleteLabel, deleteLabel)}
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
