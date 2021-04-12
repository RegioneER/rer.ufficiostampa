import React, { useState } from 'react';
import TranslationsWrapper from '../TranslationsContext';
import ApiWrapper from '../ApiContext';
import Menu from './Menu/Menu';
import UsersList from './UsersList/UsersList';
import HistoryList from './HistoryList/HistoryList';
import EditUser from './EditUser/EditUser';
import './App.less';

const App = ({ appType }) => {
  const [user, setUser] = useState(null);
  const endpoint = appType == 'history' ? 'send-history' : 'subscriptions';

  let children = null;
  if (appType == 'channels') {
    children = (
      <React.Fragment>
        <Menu editUser={() => setUser({})} />
        <UsersList editUser={u => setUser(u)} />
        <EditUser user={user} />
      </React.Fragment>
    );
  } else {
    children = (
      <React.Fragment>
        <HistoryList />
      </React.Fragment>
    );
  }

  return (
    <TranslationsWrapper>
      <ApiWrapper endpoint={endpoint}>{children}</ApiWrapper>
    </TranslationsWrapper>
  );
};
export default App;
