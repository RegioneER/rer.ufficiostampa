import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TranslationsWrapper from './TranslationsContext';
import SubscriptionsWrapper from './SubscriptionsContext';

import Menu from './Menu/Menu';
import UsersList from './UsersList/UsersList';
import EditUser from './EditUser/EditUser';
import './App.less';

const App = () => {
  const [user, setUser] = useState(null);

  return (
    <TranslationsWrapper>
      <SubscriptionsWrapper>
        <Menu editUser={() => setUser({})} />
        <UsersList />
        <EditUser user={user} />
      </SubscriptionsWrapper>
    </TranslationsWrapper>
  );
};
export default App;
