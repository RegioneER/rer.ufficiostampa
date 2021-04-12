import React, { useContext } from 'react';
import { TranslationsContext } from '../../TranslationsContext';
import { ApiContext } from '../../ApiContext';
import apiFetch from '../../utils/apiFetch';
import './Menu.less';

const Menu = ({ editUser }) => {
  const getTranslationFor = useContext(TranslationsContext);
  const { portalUrl, fetchApi, handleApiResponse, apiErrors } = useContext(
    ApiContext,
  );

  const deleteAllUsers = () => {
    if (
      window.confirm(
        getTranslationFor(
          'Are you sure you want to delete all subscribed users?',
          'Are you sure you want to delete all subscribed users?',
        ),
      )
    ) {
      let fetches = [
        apiFetch({
          url: portalUrl + '/@subscriptions-clear',
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
        <button
          onClick={() => editUser()}
          className="plone-btn plone-btn-primary"
        >
          {getTranslationFor('Add Subscriber', 'Add subscriber')}
        </button>
        <button
          onClick={() => deleteAllUsers()}
          className="plone-btn plone-btn-danger"
        >
          {getTranslationFor(
            'Delete all subscribers',
            'Delete all subscribers',
          )}
        </button>
      </div>

      {apiErrors && (
        <div className="errors">
          <dl class="portalMessage error" role="alert">
            <dt>Error. Status code: {apiErrors.status}</dt>
            <dd>{apiErrors.statusText}</dd>
          </dl>
        </div>
      )}
    </>
  );
};
export default Menu;
