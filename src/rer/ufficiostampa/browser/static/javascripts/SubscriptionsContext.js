import React, { useState, useEffect } from 'react';
import { array } from 'prop-types';

import apiFetch from './utils/apiFetch';

export const SubscriptionsContext = React.createContext({});

export const SubscriptionsProvider = SubscriptionsContext.Provider;
export const SubscriptionsConsumer = SubscriptionsContext.Consumer;

const DEFAULT_B_SIZE = 20;

function SubscriptionsWrapper({ children }) {
  const [subscriptions, setSubscriptions] = useState({});
  const [portalUrl, setPortalUrl] = useState(null);

  const fetchSubscriptions = (b_size = DEFAULT_B_SIZE, b_start = 0) => {
    const fetches = [
      apiFetch({
        url: portalUrl + '/@subscriptions',
        params: {
          b_size: b_size,
          b_start: b_start,
        },
        method: 'GET',
      }),
    ];

    Promise.all(fetches).then(data => {
      setSubscriptions(data[0].data);
    });
  };

  useEffect(() => {
    const portalUrl = document
      .querySelector('body')
      .getAttribute('data-portal-url');
    if (!portalUrl) {
      return;
    }

    setPortalUrl(portalUrl);
  }, []);

  useEffect(() => {
    if (portalUrl) {
      fetchSubscriptions();
    }
  }, [portalUrl]);

  return (
    <SubscriptionsProvider
      value={{ fetchSubscriptions, subscriptions, portalUrl }}
    >
      {children}
    </SubscriptionsProvider>
  );
}

SubscriptionsWrapper.propTypes = {
  children: array,
};

export default SubscriptionsWrapper;
